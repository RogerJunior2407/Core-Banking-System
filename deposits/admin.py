from django.contrib import admin

from .models import Deposit


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'amount', 'channel', 'is_confirmed', 'confirmed_at', 'created_at')
    list_filter = ('is_confirmed', 'channel')
    search_fields = ('wallet__id', 'wallet__client__name')
    ordering = ('-created_at',)

    @admin.action(description='Confirm selected deposits')
    def confirm_selected(self, request, queryset):
        for deposit in queryset:
            deposit.confirm()

    actions = [confirm_selected]
