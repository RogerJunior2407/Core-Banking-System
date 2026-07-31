from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClientViewSet,
    WalletViewSet,
    WalletBalanceView,
    LoginView,
    SetPasswordView,
    logout_view,
)

router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'wallets', WalletViewSet, basename='wallet')

urlpatterns = [
    path('', include(router.urls)),
    path('wallets/<int:pk>/balance/', WalletBalanceView.as_view(), name='wallet-balance'),
    path('login/', LoginView.as_view(), name='client-login'),
    path('set-password/', SetPasswordView.as_view(), name='client-set-password'),
    path('logout/', logout_view, name='client-logout'),
]