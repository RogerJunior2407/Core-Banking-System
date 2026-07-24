from django.db import models
from bank.models import Wallet


class Deposit(models.Model):
    CHANNEL_CHOICES = [
        ('CASH', 'Cash'),
        ('MOBILE_MONEY', 'Mobile Money'),
        ('BANK_TRANSFER', 'Bank Transfer'),
    ]

    wallet = models.ForeignKey(Wallet, related_name='deposits', on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    channel = models.CharField(max_length=30, choices=CHANNEL_CHOICES, default='CASH')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Deposit {self.amount} -> {self.wallet}"