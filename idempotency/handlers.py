import hashlib
import json

from django.db import IntegrityError
from django.db import transaction as db_transaction
from rest_framework import status
from rest_framework.response import Response

from idempotency.models import IdempotencyRecord


def hash_request(data) -> str:
    """Sort and hash body to check for duplicate requests later"""
    payload = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def run_idempotent(request, endpoint, handler):
    key = request.headers.get("Idempotency-Key")
    if not key:
        return Response(
            {"detail": "Idempotency-Key header is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    request_hash = hash_request(request.data)

    with db_transaction.atomic():
        try:
            with db_transaction.atomic():
                record = IdempotencyRecord.objects.create(
                    key=key, endpoint=endpoint, request_hash=request_hash
                )
        except IntegrityError:
            existing = IdempotencyRecord.objects.get(key=key, endpoint=endpoint)
            if existing.request_hash != request_hash:
                return Response(
                    {
                        "detail": "Idempotency-Key was already used with different parameters."
                    },
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )
            return Response(existing.response_body, status=existing.response_status)

        response = handler()

        record.response_status = response.status_code
        record.response_body = response.data
        record.save(update_fields=["response_status", "response_body"])

        return response
