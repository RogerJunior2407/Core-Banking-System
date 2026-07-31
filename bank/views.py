from django.views.generic import TemplateView
from rest_framework import generics, viewsets
from .models import Client, Wallet
from .serializers import ClientSerializer, WalletSerializer, WalletBalanceSerializer


class ClientPortalPageView(TemplateView):
    active_page = 'dashboard'
    page_title = 'Dashboard'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = self.active_page
        context['page_title'] = self.page_title
        return context


class ClientDashboardView(ClientPortalPageView):
    template_name = 'client/client.html'
    active_page = 'dashboard'
    page_title = 'Dashboard'


class ClientWalletView(ClientPortalPageView):
    template_name = 'client/wallet.html'
    active_page = 'wallet'
    page_title = 'Wallet'


class ClientDepositView(ClientPortalPageView):
    template_name = 'client/deposit.html'
    active_page = 'deposit'
    page_title = 'Deposit'


class ClientTransferView(ClientPortalPageView):
    template_name = 'client/transfer.html'
    active_page = 'transfer'
    page_title = 'Transfer'


class ClientReportView(ClientPortalPageView):
    template_name = 'client/report.html'
    active_page = 'report'
    page_title = 'Reports'


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer


class WalletBalanceView(generics.RetrieveAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletBalanceSerializer
    