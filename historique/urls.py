from django.urls import path
from .views import ClientTransactionHistoryView, ClientTransactionStatsView

urlpatterns = [
    path('clients/<int:client_id>/transactions/', ClientTransactionHistoryView.as_view(), name='client-transactions'),
    path('clients/<int:client_id>/transactions/stats/', ClientTransactionStatsView.as_view(), name='client-transaction-stats'),
]