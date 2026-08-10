from django.contrib import admin, messages

from .models import Deposit


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'amount', 'channel', 'status_display', 'confirmed_at', 'created_at')
    list_filter = ('is_confirmed', 'channel')
    search_fields = ('wallet__id', 'wallet__client__name')
    ordering = ('-created_at',)

    def status_display(self, obj):
        return 'Confirmed' if obj.is_confirmed else 'Pending'

    status_display.short_description = 'Status'

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
