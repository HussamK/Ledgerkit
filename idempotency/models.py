from django.db import models


class IdempotencyRecord(models.Model):
    key = models.CharField(max_length=255)
    endpoint = models.CharField(max_length=100)
    request_hash = models.CharField(max_length=64)
    response_status = models.PositiveSmallIntegerField(null=True)
    response_body = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["key", "endpoint"], name="idempotency_key_per_endpoint"
            )
        ]
