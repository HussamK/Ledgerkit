from rest_framework import serializers

from payouts.models import Obligation, Recipient


class CreateRecipientSerializer(serializers.Serializer):
    # Use Account,reference "Payable:" for 8 chars, Account.reference max_length is 100
    external_ref = serializers.CharField(max_length=92)
    name = serializers.CharField(max_length=200)


class RecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipient
        fields = ["id", "external_ref", "name", "created_at"]


class CreateObligationSerializer(serializers.Serializer):
    recipient = serializers.CharField(max_length=100)
    amount_cents = serializers.IntegerField(min_value=1)


class ObligationSerializer(serializers.ModelSerializer):
    recipient = serializers.CharField(source="recipient.external_ref", read_only=True)

    class Meta:
        model = Obligation
        fields = ["id", "recipient", "status", "amount_cents", "created_at"]
