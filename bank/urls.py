from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ChangePasswordView,
    ClientAuthView,
    ClientDashboardView,
    ClientDepositView,
    ClientPaymentView,
    ClientReportView,
    ClientTransferView,
    ClientViewSet,
    ClientWalletView,
    CreateWalletView,
    SetPasswordView,
    WalletBalanceView,
    WalletViewSet,
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
    path('<uuid:client_id>/dashboard/', ClientDashboardView.as_view(), name='client-dashboard-by-id'),
    path('wallet/', ClientWalletView.as_view(), name='client-wallet'),
    path('<uuid:client_id>/wallet/', ClientWalletView.as_view(), name='client-wallet-by-id'),
    path('deposit/', ClientDepositView.as_view(), name='client-deposit'),
    path('<uuid:client_id>/deposit/', ClientDepositView.as_view(), name='client-deposit-by-id'),
    path('transfer/', ClientTransferView.as_view(), name='client-transfer'),
    path('<uuid:client_id>/transfer/', ClientTransferView.as_view(), name='client-transfer-by-id'),
    path('payment/', ClientPaymentView.as_view(), name='client-payment'),
    path('<uuid:client_id>/payment/', ClientPaymentView.as_view(), name='client-payment-by-id'),
    path('change-password/', ChangePasswordView.as_view(), name='client-change-password'),
    path('<uuid:client_id>/change-password/', ChangePasswordView.as_view(), name='client-change-password-by-id'),
    path('report/', ClientReportView.as_view(), name='client-report'),
    path('<uuid:client_id>/report/', ClientReportView.as_view(), name='client-report-by-id'),
    path('login/', ClientAuthView.as_view(), name='client-login'),
    path('signup/', ClientAuthView.as_view(), name='client-signup'),
    path('auth/', ClientAuthView.as_view(), name='client-auth'),
    path('wallet/create/', CreateWalletView.as_view(), name='create-wallet'),
  
]