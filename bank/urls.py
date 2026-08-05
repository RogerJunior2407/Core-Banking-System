from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientAuthView, CreateWalletView,  SetPasswordView, logout_view, ClientDashboardView, ClientWalletView, ClientDepositView, ClientTransferView, ClientPaymentView, ClientReportView
from .views import (
    ClientViewSet,
    WalletViewSet,
    WalletBalanceView,
    SetPasswordView,
    ChangePasswordView,
    logout_view,
)


router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'wallets', WalletViewSet, basename='wallet')

urlpatterns = [
    path('', include(router.urls)),
    path('wallets/<int:pk>/balance/', WalletBalanceView.as_view(), name='wallet-balance'),
    path('set-password/', SetPasswordView.as_view(), name='client-set-password'),
    path('logout/', logout_view, name='client-logout'),
    path('dashboard/', ClientDashboardView.as_view(), name='client-dashboard'),
    path('wallet/', ClientWalletView.as_view(), name='client-wallet'),
    path('deposit/', ClientDepositView.as_view(), name='client-deposit'),
    path('transfer/', ClientTransferView.as_view(), name='client-transfer'),
    path('payment/', ClientPaymentView.as_view(), name='client-payment'),
    path('change-password/', ChangePasswordView.as_view(), name='client-change-password'),
    path('report/', ClientReportView.as_view(), name='client-report'),
    path('login/', ClientAuthView.as_view(), name='client-login'),
    path('signup/', ClientAuthView.as_view(), name='client-signup'),
    path('auth/', ClientAuthView.as_view(), name='client-auth'),
    path('wallet/create/', CreateWalletView.as_view(), name='create-wallet'),
  
]