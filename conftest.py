import pytest
from rest_framework.test import APIClient

from ledger.models import Account
from payouts.services import create_recipient


@pytest.fixture
def platform_cash(db):
    return Account.objects.create(kind=Account.Kind.CASH, reference="Platform:Cash")


@pytest.fixture
def external_provider(db):
    return Account.objects.create(
        kind=Account.Kind.EXTERNAL, reference="External:Provider"
    )


@pytest.fixture
def ana_payable(db):
    return Account.objects.create(kind=Account.Kind.PAYABLE, reference="Ana:Payable")


@pytest.fixture
def ana(db):
    return create_recipient(external_ref="ana-123", name="Ana")


@pytest.fixture
def api_client():
    return APIClient()
