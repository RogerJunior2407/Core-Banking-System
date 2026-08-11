from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html

from .models import Deposit


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'amount', 'channel', 'status_display', 'client_portal_link', 'confirmed_at', 'created_at')
    list_filter = ('is_confirmed', 'channel')
    search_fields = ('wallet__id', 'wallet__client__name')
    ordering = ('-created_at',)

    def status_display(self, obj):
        return 'Confirmed' if obj.is_confirmed else 'Pending'

    status_display.short_description = 'Status'

    def client_portal_link(self, obj):
        if not obj.wallet or not obj.wallet.client_id:
            return '-'
        url = reverse('client-dashboard-by-id', args=[obj.wallet.client_id])
        return format_html('<a href="{}" target="_blank">Open client portal</a>', url)

    client_portal_link.short_description = 'Client portal'

    @admin.action(description='Confirm selected deposits')
    def confirm_selected(self, request, queryset):
        pending = queryset.filter(is_confirmed=False)
        count = 0
        for deposit in pending:
            deposit.confirm()
            count += 1

        if count:
            self.message_user(request, f'{count} deposit(s) confirmed successfully.', messages.SUCCESS)
        else:
            self.message_user(request, 'No pending deposits selected.', messages.WARNING)

    actions = [confirm_selected]
