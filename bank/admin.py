from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import ClientAuth, Client, Wallet


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'portal_link')
    search_fields = ('name', 'phone')

    def portal_link(self, obj):
        url = reverse('client-dashboard-by-id', args=[obj.id])
        return format_html('<a href="{}" target="_blank">Open portal</a>', url)

    portal_link.short_description = 'Client portal'


admin.site.register(ClientAuth)
admin.site.register(Wallet)