import pytest

from ledger.models import Account

@pytest.fixture
def platform_cash(db):
    return Account.objects.create(
        kind=Account.Kind.CASH, reference="Platform:Cash"
    )

@pytest.fixture
def external_provider(db):
    return Account.objects.create(
        kind=Account.Kind.EXTERNAL, reference="External:Provider"
    )

@pytest.fixture
def ana_payable(db):
    return Account.objects.create(
        kind=Account.Kind.PAYABLE, reference="Ana:Payable"
    )
