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
        serializer.save()