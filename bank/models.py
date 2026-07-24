from django.db import models
import uuid

class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)
    adress = models.CharField()
    phone = models.CharField(max_length=20)
    
        








class Wallet(models.Model):
       client = models.ForeignKey(Client, related_name="wallets", on_delete=models.CASCADE)
       balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
       currency = models.CharField(max_length=3, default="fbi")

  
    
