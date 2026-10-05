import pytest

from ledger.models import Account
from payouts.models import Recipient


@pytest.mark.django_db
def test_create_recipient_returns_201(api_client):
    response = api_client.post(
        "/api/recipients/", {"external_ref": "ana-123", "name": "Ana"}, format="json"
    )

    assert response.status_code == 201
    assert response.data["external_ref"] == "ana-123"


@pytest.mark.django_db
def test_duplicate_create_recipient_returns_409(api_client):
    api_client.post(
        "/api/recipients/", {"external_ref": "ana-123", "name": "Ana"}, format="json"
    )

    response = api_client.post(
        "/api/recipients/", {"external_ref": "ana-123", "name": "Ana"}, format="json"
    )

    assert response.status_code == 409
    assert Recipient.objects.count() == 1
    assert Account.objects.filter(kind=Account.Kind.PAYABLE).count() == 1


@pytest.mark.django_db
def test_no_name_create_recipient_returns_400(api_client):
    response = api_client.post(
        "/api/recipients/", {"external_ref": "ana-123"}, format="json"
    )

    assert response.status_code == 400
    assert "name" in response.data
