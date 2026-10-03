from django.db import transaction as db_transaction

from payouts.models import Obligation, Recipient
from ledger.models import Account
from ledger.services import record_transaction

def create_recipient(external_ref: str, name:str) -> Recipient:
    with db_transaction.atomic():
        account = Account.objects.create(
            kind=Account.Kind.PAYABLE, 
            reference=f"Payable:{external_ref}",
        )
        recipient = Recipient.objects.create(
            external_ref = external_ref,
            name=name,
            payable_account=account
        )
    return recipient

def create_obligation(recipient: Recipient, amount_cents: int) -> Obligation:
    if amount_cents <= 0:
        raise ValueError("Obligation amount must be specified")
    
    with db_transaction.atomic():
        platform_cash = Account.objects.get(reference="Platform:Cash")
        legs = [
            (platform_cash, -amount_cents),
            (recipient.payable_account, amount_cents)
        ]
        obligation_txn = record_transaction("obligation_recorded", legs)
        obligation = Obligation.objects.create(
            recipient=recipient, 
            amount_cents=amount_cents, 
            recorded_transaction=obligation_txn
        )
        return obligation