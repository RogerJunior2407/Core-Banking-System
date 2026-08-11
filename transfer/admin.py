from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html

from .models import Transfer


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ('source_wallet', 'destination_wallet', 'amount', 'status_display', 'client_portal_link', 'confirmed_at', 'created_at')
    list_filter = ('is_confirmed',)
    search_fields = ('source_wallet__id', 'destination_wallet__id', 'source_wallet__client__name')
    ordering = ('-created_at',)

    def status_display(self, obj):
        return 'Authorized' if obj.is_confirmed else 'Pending'

    status_display.short_description = 'Status'

    def client_portal_link(self, obj):
        if not obj.source_wallet or not obj.source_wallet.client_id:
            return '-'
        url = reverse('client-dashboard-by-id', args=[obj.source_wallet.client_id])
        return format_html('<a href="{}" target="_blank">Open client portal</a>', url)

    client_portal_link.short_description = 'Client portal'

    @admin.action(description='Authorize selected transfers')
    def authorize_selected(self, request, queryset):
        pending = queryset.filter(is_confirmed=False)
        count = 0
        for transfer in pending:
            transfer.authorize()
            count += 1

        if count:
            self.message_user(request, f'{count} transfer(s) authorized successfully.', messages.SUCCESS)
        else:
            self.message_user(request, 'No pending transfers selected.', messages.WARNING)

    actions = [authorize_selected]
