from django.db import IntegrityError
from django.db import transaction as db_transaction

from ledger.models import Account
from ledger.services import record_transaction
from payouts.models import Obligation, Recipient


class RecipientAlreadyExists(Exception):
    pass


def create_recipient(external_ref: str, name: str) -> Recipient:
    try:
        with db_transaction.atomic():
            account = Account.objects.create(
                kind=Account.Kind.PAYABLE,
                reference=f"Payable:{external_ref}",
            )
            recipient = Recipient.objects.create(
                external_ref=external_ref, name=name, payable_account=account
            )
    except IntegrityError as exc:
        raise RecipientAlreadyExists(external_ref) from exc
    return recipient


def create_obligation(recipient: Recipient, amount_cents: int) -> Obligation:
    if amount_cents <= 0:
        raise ValueError("Obligation amount must be positive")

    with db_transaction.atomic():
        platform_cash = Account.objects.get(reference="Platform:Cash")
        legs = [
            (platform_cash, -amount_cents),
            (recipient.payable_account, amount_cents),
        ]
        obligation_txn = record_transaction("obligation_recorded", legs)
        obligation = Obligation.objects.create(
            recipient=recipient,
            amount_cents=amount_cents,
            recorded_transaction=obligation_txn,
        )
        return obligation
