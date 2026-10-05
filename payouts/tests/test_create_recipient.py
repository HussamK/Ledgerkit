import pytest
from django.db import DataError

from ledger.models import Account
from payouts.services import create_recipient


@pytest.mark.django_db
def test_create_recipient():
    recipient = create_recipient(external_ref="ana-123", name="Ana")

    assert recipient.payable_account.reference == "Payable:ana-123"
    assert recipient.name == "Ana"
    assert recipient.external_ref == "ana-123"
    assert recipient.payable_account.kind == Account.Kind.PAYABLE
    assert recipient.payable_account.recipient == recipient


@pytest.mark.django_db
def test_large_name_create_recipient():
    with pytest.raises(DataError):
        create_recipient(external_ref="ana-123", name="x" * 201)

    assert Account.objects.filter(kind=Account.Kind.PAYABLE).count() == 0
