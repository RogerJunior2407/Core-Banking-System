from rest_framework import serializers
from .models import Transfer


class TransferSerializer(serializers.ModelSerializer):
    client_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Transfer
        fields = ['id', 'source_wallet', 'destination_wallet', 'amount', 'client_id', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        validated_data.pop('client_id', None)
        return Transfer.objects.create(**validated_data)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate(self, data):
        source = data['source_wallet']
        destination = data['destination_wallet']
        amount = data['amount']
        client_id = data.get('client_id')

        if source.pk == destination.pk:
            raise serializers.ValidationError("Source and destination wallets must be different.")

        if source.currency.lower() != destination.currency.lower():
            raise serializers.ValidationError("Source and destination wallets must have the same currency.")

        if client_id and source.client_id != client_id:
            raise serializers.ValidationError({'client_id': 'The selected source wallet does not belong to the active client.'})

        if source.balance < amount:
            raise serializers.ValidationError("Insufficient balance in source wallet.")

        return data