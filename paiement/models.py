from django.db import models
from bank.models import Wallet


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
    provider = models.ForeignKey(ServiceProvider, related_name='bills', on_delete=models.PROTECT)
    reference_number = models.CharField(max_length=100)
    amount_due = models.DecimalField(max_digits=18, decimal_places=2)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.provider} - {self.reference_number}"


class Payment(models.Model):
    wallet = models.ForeignKey(Wallet, related_name='payments', on_delete=models.PROTECT)
    bill = models.ForeignKey(Bill, related_name='payments', on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.amount} for {self.bill}"