from django.db import models
import uuid
from django import forms

class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)
    adress = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20)
    
class ClientAuth(models.Model):
    client = models.OneToOneField(Client, related_name='auth', on_delete=models.CASCADE)
    password = models.CharField(max_length=128, blank=True, null=True)

    def set_password(self, raw_password):
        from django.contrib.auth.hashers import make_password
        self.password = make_password(raw_password)
        self.save(update_fields=['password'])

    def check_password(self, raw_password):
        from django.contrib.auth.hashers import check_password
        if not self.password:
            return False
        return check_password(raw_password, self.password)

        





class Wallet(models.Model):
       client = models.ForeignKey(Client, related_name="wallets", on_delete=models.CASCADE)
       balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
       currency = models.CharField(max_length=3, default="fbi")

  
    
