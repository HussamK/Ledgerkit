import pytest
from django.db.models import Sum

from ledger.exceptions import UnbalancedTransaction
from ledger.models import Entry
from ledger.services import record_transaction


def test_writes_balanced_transaction(platform_cash, ana_payable):
    txn = record_transaction(
        kind="obligation_recorded",
        legs=[(platform_cash, -90000), (ana_payable, 90000)],
    )

    assert txn.entries.count() == 2
    assert sum(e.amount_cents for e in txn.entries.all()) == 0


def test_rejects_unbalanced_legs(platform_cash, ana_payable):
    with pytest.raises(UnbalancedTransaction):
        record_transaction(
            kind="bad",
            legs=[(platform_cash, -90000), (ana_payable, 90001)],
        )

    assert Entry.objects.count() == 0


def test_rejects_single_leg(platform_cash):
    with pytest.raises(UnbalancedTransaction):
        record_transaction(kind="bad", legs=[(platform_cash, 0)])


def test_ledger_sums_to_zero_globally(platform_cash, ana_payable):
    record_transaction(
        "obligation_recorded", [(platform_cash, -90000), (ana_payable, 90000)]
    )
    total = Entry.objects.aggregate(Sum("amount_cents"))["amount_cents__sum"]
    assert total == 0
