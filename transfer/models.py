from decimal import Decimal

from django.db import models, transaction
from django.utils import timezone

from bank.models import Wallet


class Transfer(models.Model):
    source_wallet = models.ForeignKey(Wallet, related_name='transfers_sent', on_delete=models.PROTECT)
    destination_wallet = models.ForeignKey(Wallet, related_name='transfers_received', on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(blank=True, null=True)

    def authorize(self):
        if self.is_confirmed:
            return self

        with transaction.atomic():
            source = Wallet.objects.select_for_update().get(pk=self.source_wallet_id)
            destination = Wallet.objects.select_for_update().get(pk=self.destination_wallet_id)

            if source.balance < self.amount:
                raise ValueError('Insufficient balance in source wallet.')

            source.balance -= self.amount
            destination.balance += self.amount
            source.save(update_fields=['balance'])
            destination.save(update_fields=['balance'])
            self.is_confirmed = True
            self.confirmed_at = timezone.now()
            self.save(update_fields=['is_confirmed', 'confirmed_at'])

        return self

    @property
    def is_pending(self):
        return not self.is_confirmed

    def __str__(self):
        return f"Transfer {self.amount}: {self.source_wallet} -> {self.destination_wallet}"