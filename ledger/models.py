from django.db import models
from django.db.models import Q


class Account(models.Model):
    class Kind(models.TextChoices):
        CASH = ("cash",)
        EXTERNAL = ("external",)
        PAYABLE = "payable"

    kind = models.CharField(max_length=30, choices=Kind.choices)
    reference = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.reference


class Transaction(models.Model):
    kind = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]


class Entry(models.Model):
    transaction = models.ForeignKey(
        Transaction, on_delete=models.PROTECT, related_name="entries"
    )
    account = models.ForeignKey(
        Account, on_delete=models.PROTECT, related_name="entries"
    )
    amount_cents = models.BigIntegerField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~Q(amount_cents=0),
                name="entry_amount_nonzero",
            )
        ]
