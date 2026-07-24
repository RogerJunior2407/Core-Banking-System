from django.db import models
from bank.models import Wallet


class Transfer(models.Model):
    source_wallet = models.ForeignKey(Wallet, related_name='transfers_sent', on_delete=models.PROTECT)
    destination_wallet = models.ForeignKey(Wallet, related_name='transfers_received', on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transfer {self.amount}: {self.source_wallet} -> {self.destination_wallet}"