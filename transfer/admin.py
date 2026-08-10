from django.contrib import admin

from .models import Transfer


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ('source_wallet', 'destination_wallet', 'amount', 'is_confirmed', 'confirmed_at', 'created_at')
    list_filter = ('is_confirmed',)
    search_fields = ('source_wallet__id', 'destination_wallet__id', 'source_wallet__client__name')
    ordering = ('-created_at',)

    @admin.action(description='Authorize selected transfers')
    def authorize_selected(self, request, queryset):
        for transfer in queryset:
            transfer.authorize()

    actions = [authorize_selected]
