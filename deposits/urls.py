from django.urls import path
from .views import DepositListCreateView

urlpatterns = [
    path('', DepositListCreateView.as_view(), name='deposit-list-create'),
]