from django.db import transaction
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Deposit
from .serializers import DepositSerializer


class DepositListCreateView(generics.ListCreateAPIView):
    queryset = Deposit.objects.select_related('wallet').all()
    serializer_class = DepositSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['wallet', 'channel']
    ordering_fields = ['created_at', 'amount']

    def perform_create(self, serializer):
        with transaction.atomic():
            wallet = serializer.validated_data['wallet']
            wallet = type(wallet).objects.select_for_update().get(pk=wallet.pk)
            deposit = serializer.save()
            wallet.balance += deposit.amount
            wallet.save(update_fields=['balance'])