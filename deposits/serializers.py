from rest_framework import serializers
from .models import Deposit


class DepositSerializer(serializers.ModelSerializer):
    client_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Deposit
        fields = ['id', 'wallet', 'amount', 'channel', 'client_id', 'created_at', 'is_confirmed', 'confirmed_at']
        read_only_fields = ['id', 'created_at', 'is_confirmed', 'confirmed_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate(self, data):
        wallet = data.get('wallet')
        client_id = data.get('client_id')

        if wallet and client_id and wallet.client_id != client_id:
            raise serializers.ValidationError({'client_id': 'The selected wallet does not belong to the active client.'})

        return data