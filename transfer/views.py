from django.db import transaction
from rest_framework import generics, filters , serializers
from django_filters.rest_framework import DjangoFilterBackend
from bank.models import Wallet
from .models import Transfer
from .serializers import TransferSerializer


class TransferListCreateView(generics.ListCreateAPIView):
    queryset = Transfer.objects.select_related('source_wallet', 'destination_wallet').all()
    serializer_class = TransferSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['source_wallet', 'destination_wallet']
    ordering_fields = ['created_at', 'amount']

    def perform_create(self, serializer):
        with transaction.atomic():
            source = serializer.validated_data['source_wallet']
            destination = serializer.validated_data['destination_wallet']
            amount = serializer.validated_data['amount']

            # lock both rows to prevent race conditions on concurrent transfers
            source = Wallet.objects.select_for_update().get(pk=source.pk)
            destination = Wallet.objects.select_for_update().get(pk=destination.pk)

            if source.balance < amount:
                raise serializers.ValidationError("Insufficient balance in source wallet.")

            source.balance -= amount
            destination.balance += amount
            source.save(update_fields=['balance'])
            destination.save(update_fields=['balance'])

            serializer.save()