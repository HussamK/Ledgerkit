from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from idempotency.handlers import run_idempotent
from payouts.models import Recipient
from payouts.serializers import (
    CreateObligationSerializer,
    CreateRecipientSerializer,
    ObligationSerializer,
    RecipientSerializer,
)
from payouts.services import RecipientAlreadyExists, create_obligation, create_recipient


class RecipientCreateView(APIView):
    def post(self, request):
        input_serializer = CreateRecipientSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            recipient = create_recipient(**input_serializer.validated_data)
        except RecipientAlreadyExists:
            return Response(
                {"detail": "Recipient already exists."}, status=status.HTTP_409_CONFLICT
            )

        return Response(
            RecipientSerializer(recipient).data,
            status=status.HTTP_201_CREATED,
        )


class ObligationCreateView(APIView):
    def post(self, request):
        return run_idempotent(
            request,
            endpoint="POST /obligations",
            handler=lambda: self.create_obligation(request),
        )

    def create_obligation(self, request):
        input_serializer = CreateObligationSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data
        recipient = get_object_or_404(Recipient, external_ref=data["recipient"])
        obligation = create_obligation(recipient, data["amount_cents"])

        return Response(
            ObligationSerializer(obligation).data,
            status=status.HTTP_201_CREATED,
        )
