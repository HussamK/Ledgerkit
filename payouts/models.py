from django.db import models
from django.db.models import Q

from ledger.models import Account, Transaction


class Recipient(models.Model):
    external_ref = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    payable_account = models.OneToOneField(
        Account, on_delete=models.PROTECT, related_name="recipient"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Obligation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending"
        BATCHED = "batched"
        PAID = "paid"
        FAILED = "failed"
        UNRESOLVED = "unresolved"

    recipient = models.ForeignKey(
        Recipient, on_delete=models.PROTECT, related_name="obligations"
    )
    amount_cents = models.BigIntegerField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    recorded_transaction = models.OneToOneField(
        Transaction, on_delete=models.PROTECT, related_name="+"
    )
    settled_transaction = models.OneToOneField(
        Transaction,
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(amount_cents__gt=0), name="obligation_amount_positive"
            )
        ]
