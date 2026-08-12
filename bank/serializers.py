# apps/clients/serializers.py
from rest_framework import serializers
from .models import Client, Wallet


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'client', 'balance', 'currency']
        read_only_fields = ['id', 'balance'] 


class ClientSerializer(serializers.ModelSerializer):
    wallets = WalletSerializer(many=True, read_only=True)

    class Meta:
        model = Client
        fields = ['id', 'name', 'age', 'adress', 'phone', 'wallets']
    
        
        
        
        
class WalletBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'balance', 'currency']        
        
        
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, write_only=True)
    new_password = serializers.CharField(max_length=128, write_only=True)

    def validate_old_password(self, value):
        auth = getattr(self.instance, 'auth', self.instance)
        if auth is None or not auth.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("New password must be at least 8 characters long.")
        return value

    def update(self, instance, validated_data):
        new_password = validated_data.get('new_password')
        instance.set_password(new_password)
        return instance