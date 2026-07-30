from rest_framework import serializers
from .models import Transfer


class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = ['id', 'source_wallet', 'destination_wallet', 'amount', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate(self, data):
        source = data['source_wallet']
        destination = data['destination_wallet']
        amount = data['amount']

        if source.pk == destination.pk:
            raise serializers.ValidationError("Source and destination wallets must be different.")

        if source.currency.lower() != destination.currency.lower():
            raise serializers.ValidationError("Source and destination wallets must have the same currency.")

        if source.balance < amount:
            raise serializers.ValidationError("Insufficient balance in source wallet.")

        return data