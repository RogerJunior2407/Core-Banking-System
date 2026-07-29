from django.db import transaction
from rest_framework import generics, filters, serializers
from django_filters.rest_framework import DjangoFilterBackend
from bank.models import Wallet
from .models import ServiceProvider, Bill, Payment
from .serializers import ServiceProviderSerializer, BillSerializer, PaymentSerializer


class ServiceProviderViewSet(generics.ListCreateAPIView):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer


class BillListCreateView(generics.ListCreateAPIView):
    queryset = Bill.objects.select_related('provider').all()
    serializer_class = BillSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['provider', 'is_paid']



class PaymentListCreateView(generics.ListCreateAPIView):
    queryset = Payment.objects.select_related('wallet', 'bill').all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['wallet', 'bill']
    ordering_fields = ['created_at', 'amount']

    def perform_create(self, serializer):
        with transaction.atomic():
            wallet = serializer.validated_data['wallet']
            bill = serializer.validated_data['bill']
            amount = serializer.validated_data['amount']

            wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)

            if wallet.balance < amount:
                raise serializers.ValidationError("Solde insuffisant.")

            wallet.balance -= amount
            wallet.save(update_fields=['balance'])

            bill.is_paid = True
            bill.save(update_fields=['is_paid'])

            serializer.save()