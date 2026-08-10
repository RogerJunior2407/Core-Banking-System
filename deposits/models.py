from django.db import models, transaction
from django.utils import timezone

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
    is_confirmed = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(blank=True, null=True)

    def confirm(self):
        if self.is_confirmed:
            return self

        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(pk=self.wallet_id)
            wallet.balance += self.amount
            wallet.save(update_fields=['balance'])
            self.is_confirmed = True
            self.confirmed_at = timezone.now()
            self.save(update_fields=['is_confirmed', 'confirmed_at'])

        return self

    @property
    def is_pending(self):
        return not self.is_confirmed

    def __str__(self):
        return f"Deposit {self.amount} -> {self.wallet}"