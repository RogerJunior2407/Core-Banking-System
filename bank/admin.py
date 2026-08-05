from django.contrib import admin
from .models import ClientAuth , Client ,Wallet

admin.site.register(ClientAuth)
admin.site.register(Client)
admin.site.register(Wallet)