from django.contrib import admin

from .models import Bill, Payment, ServiceProvider


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name', 'category')


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'client', 'provider', 'amount_due', 'currency', 'is_paid')
    list_filter = ('is_paid', 'provider', 'currency')
    search_fields = ('reference_number', 'client__name', 'provider__name')
    list_select_related = ('client', 'provider')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('bill', 'wallet', 'amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('bill__reference_number', 'wallet__currency')
