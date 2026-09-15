from django.db import transaction as db_transaction
from ledger.models import Account, Entry, Transaction

from ledger.exceptions import UnbalancedTransaction

def record_transaction(kind:str, legs: list[tuple[Account, int]]) -> Transaction:
    """Write a balanced transaction to the ledger.

    This is the only sanctioned way to write entries. Every transaction must
    consist of at least two legs whose amounts sum to exactly zero money is
    always moved between accounts, never created or destroyed. An unbalanced
    set of legs is rejected before anything is written.

    Amounts are signed integers in cents. A negative amount decreases the
    account, a positive amount increases it. Integer cents avoid the rounding
    errors that floats and decimals introduce into repeated arithmetic.

    The transaction and all its entries are written in a single atomic block.

    Args:
        kind: What financial event this records, e.g. "obligation_recorded"
            or "payout_settled". Stored for audit and reporting.
        legs: Account and signed amount-in-cents pairs. Must contain at least
            two entries summing to zero.

    Returns:
        The created Transaction, with its entries accessible via `.entries`.

    Raises:
        UnbalancedTransaction: If the legs sum to a non-zero value or fewer
            than two legs are supplied.
    """
    # Validate legs
    if len(legs) < 2:
        raise UnbalancedTransaction("A transaction needs at least 2 legs")

    total = sum(amount for _, amount in legs)

    if total != 0:
        raise UnbalancedTransaction(f"Legs must sum to zero, got {total}")

    with db_transaction.atomic():
        ledger_transaction = Transaction.objects.create(kind=kind)

        for account, amount in legs:
            Entry.objects.create(
                transaction=ledger_transaction,
                account=account,
                amount_cents=amount
            )

        return ledger_transaction