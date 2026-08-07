from rest_framework import serializers
from .models import ServiceProvider, Bill, Payment


class ServiceProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvider
        fields = ['id', 'name', 'category']


class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = ['id', 'client', 'provider', 'reference_number', 'amount_due', 'currency', 'is_paid']
        read_only_fields = ['id', 'is_paid']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'wallet', 'bill', 'amount', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        wallet = data['wallet']
        bill = data['bill']
        amount = data['amount']

        if amount <= 0:
            raise serializers.ValidationError("Le montant doit être supérieur à zéro.")
        if bill.is_paid:
            raise serializers.ValidationError("Cette facture est déjà payée.")
        if wallet.balance < amount:
            raise serializers.ValidationError("Solde insuffisant.")

        return data