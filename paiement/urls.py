from django.urls import path
from .views import ServiceProviderViewSet, BillListCreateView, PaymentListCreateView

urlpatterns = [
    path('providers/', ServiceProviderViewSet.as_view(), name='provider-list-create'),
    path('bills/', BillListCreateView.as_view(), name='bill-list-create'),
    path('payments/', PaymentListCreateView.as_view(), name='payment-list-create'),
]