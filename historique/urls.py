from django.urls import path
from .views import ClientTransactionHistoryView, ClientTransactionStatsView

urlpatterns = [
    path('clients/<uuid:client_id>/transactions/', ClientTransactionHistoryView.as_view(), name='client-transactions'),
    path('clients/<uuid:client_id>/transactions/stats/', ClientTransactionStatsView.as_view(), name='client-transaction-stats'),
]