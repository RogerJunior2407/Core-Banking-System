from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, WalletViewSet, WalletBalanceView

router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'wallets', WalletViewSet, basename='wallet')

urlpatterns = [
    path('', include(router.urls)),
    path('wallets/<int:pk>/balance/', WalletBalanceView.as_view(), name='wallet-balance'),
]