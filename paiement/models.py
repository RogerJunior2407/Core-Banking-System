from decimal import Decimal

from django.db import models
from django.db.models import Sum

from bank.models import Client, Wallet


CURRENCY_CHOICES = [
    ('USD', 'USD'),
    ('EUR', 'EUR'),
    ('GBP', 'GBP'),
    ('MAD', 'MAD'),
    ('FBI', 'FBI'),
]


class ServiceProvider(models.Model):
    CATEGORY_CHOICES = [
        ('ELECTRICITY', 'Électricité'),
        ('WATER', 'Eau'),
        ('INTERNET', 'Internet'),
        ('TV', 'Télévision'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.name


class Bill(models.Model):
    client = models.ForeignKey(Client, related_name='bills', on_delete=models.PROTECT)
    provider = models.ForeignKey(ServiceProvider, related_name='bills', on_delete=models.PROTECT)
    reference_number = models.CharField(max_length=100)
    amount_due = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    is_paid = models.BooleanField(default=False)

    @property
    def total_paid(self):
        total = self.payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        return total

    @property
    def remaining_amount(self):
        amount_due = self.amount_due if isinstance(self.amount_due, Decimal) else Decimal(str(self.amount_due))
        return max(amount_due - self.total_paid, Decimal('0.00'))

    def __str__(self):
        return f"{self.provider} - {self.reference_number} ({self.currency})"


class Payment(models.Model):
    wallet = models.ForeignKey(Wallet, related_name='payments', on_delete=models.PROTECT)
    bill = models.ForeignKey(Bill, related_name='payments', on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.amount} for {self.bill}"