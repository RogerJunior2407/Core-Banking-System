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
        
        
        
        