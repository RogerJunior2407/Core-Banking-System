from django.db import models
import uuid
from django.contrib.auth.hashers import make_password, check_password

class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)
    adress = models.CharField()
    phone = models.CharField(max_length=13)
    password = models.CharField(max_length = 20)
    phone = models.CharField(max_length=20, unique=True)
    
    def set_password(self,raw_password):
        self.password= make_password(raw_password)
        
    def check_password(self,raw_password):
        return check_password(raw_password,self.password)
        








class Wallet(models.Model):
       client = models.ForeignKey(Client, related_name="wallets", on_delete=models.CASCADE)
       balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
       currency = models.CharField(max_length=3, default="fbi")

  
    
