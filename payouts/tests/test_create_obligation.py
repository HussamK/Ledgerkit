import pytest

from django.db.models import Sum, Q
from django.db import IntegrityError

from ledger.models import Entry
from payouts.models import Obligation
from payouts.services import create_obligation


def test_create_obligation(ana, platform_cash):
    obligation = create_obligation(ana, 100)

    assert obligation.recipient == ana
    assert obligation.amount_cents == 100
    assert obligation.status == Obligation.Status.PENDING
    assert obligation.recorded_transaction is not None
    
def test_total_obligation(ana, platform_cash):
    create_obligation(ana, 100)
    totals = Entry.objects.aggregate(
        ana_total=Sum("amount_cents", filter=Q(account=ana.payable_account)),
        cash_total=Sum("amount_cents", filter=Q(account=platform_cash))
    )
    
    assert totals["ana_total"] == 100
    assert totals["cash_total"] == -100

@pytest.mark.parametrize("amount_cents", [-100,0])
def test_rejects_non_positive_amount(ana, platform_cash, amount_cents):
    with pytest.raises(ValueError):
        create_obligation(ana, amount_cents)

    assert Entry.objects.count() == 0

def test_obligation_failure_rolls_back_ledger(ana, platform_cash, monkeypatch):
    def always_fails(**kwargs):
        raise IntegrityError("Forced failure for test")

    monkeypatch.setattr(Obligation.objects, "create", always_fails)

    with pytest.raises(IntegrityError):
        create_obligation(ana, 100)

    assert Entry.objects.count() == 0