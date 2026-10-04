import pytest

from idempotency.models import IdempotencyRecord
from ledger.models import Entry
from payouts.models import Obligation


@pytest.mark.django_db
def test_create_obligation_returns_201(api_client, ana, platform_cash):
    response = api_client.post(
        "/api/obligations/",
        {"recipient": ana.external_ref, "amount_cents": 90000},
        format="json",
        HTTP_IDEMPOTENCY_KEY="key-1",
    )

    assert response.status_code == 201
    assert response.data["recipient"] == ana.external_ref
    assert response.data["amount_cents"] == 90000
    assert response.data["status"] == "pending"
    assert Obligation.objects.count() == 1


@pytest.mark.django_db
def test_different_parameters_create_obligation_returns_422(
    api_client, ana, platform_cash
):
    api_client.post(
        "/api/obligations/",
        {"recipient": ana.external_ref, "amount_cents": 90000},
        format="json",
        HTTP_IDEMPOTENCY_KEY="key-1",
    )

    response = api_client.post(
        "/api/obligations/",
        {"recipient": ana.external_ref, "amount_cents": 50000},
        format="json",
        HTTP_IDEMPOTENCY_KEY="key-1",
    )

    assert response.status_code == 422
    assert "detail" in response.data
    assert Obligation.objects.count() == 1
    assert Obligation.objects.get().amount_cents == 90000


@pytest.mark.django_db
def test_retry_with_same_key_replays_original(api_client, ana, platform_cash):
    first = api_client.post(
        "/api/obligations/",
        {"recipient": ana.external_ref, "amount_cents": 90000},
        format="json",
        HTTP_IDEMPOTENCY_KEY="key-1",
    )

    second = api_client.post(
        "/api/obligations/",
        {"recipient": ana.external_ref, "amount_cents": 90000},
        format="json",
        HTTP_IDEMPOTENCY_KEY="key-1",
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert second.data["id"] == first.data["id"]
    assert Obligation.objects.count() == 1
    assert Entry.objects.count() == 2


@pytest.mark.parametrize(
    "body, bad_field",
    [
        ({"amount_cents": 90000}, "recipient"),
        ({"recipient": "ana-123"}, "amount_cents"),
        ({"recipient": "ana-123", "amount_cents": 0}, "amount_cents"),
        ({"recipient": "ana-123", "amount_cents": -500}, "amount_cents"),
        ({"recipient": "ana-123", "amount_cents": "abc"}, "amount_cents"),
    ],
)
@pytest.mark.django_db
def test_invalid_body_returns_400(api_client, body, bad_field):
    response = api_client.post(
        "/api/obligations/", body, format="json", HTTP_IDEMPOTENCY_KEY="key-1"
    )

    assert response.status_code == 400
    assert bad_field in response.data
    assert IdempotencyRecord.objects.count() == 0


@pytest.mark.django_db
def test_recipient_does_not_exist_returns_404(api_client):
    response = api_client.post(
        "/api/obligations/",
        {"recipient": "Steve", "amount_cents": 90000},
        format="json",
        HTTP_IDEMPOTENCY_KEY="key-1",
    )

    assert response.status_code == 404
    assert Obligation.objects.count() == 0
    assert Entry.objects.count() == 0
    assert IdempotencyRecord.objects.count() == 0


@pytest.mark.django_db
def test_missing_idempotency_key(api_client, ana, platform_cash):
    response = api_client.post(
        "/api/obligations/",
        {"recipient": ana.external_ref, "amount_cents": 50000},
        format="json",
    )

    assert response.status_code == 400
    assert Obligation.objects.count() == 0
