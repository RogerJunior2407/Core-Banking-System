from django.views.generic import TemplateView, FormView
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django import forms
from rest_framework import generics, viewsets
from .models import Client, Wallet, ClientAuth
from .serializers import ClientSerializer, WalletSerializer, WalletBalanceSerializer
from django.contrib import messages


class ClientPortalPageView(TemplateView):
    active_page = 'dashboard'
    page_title = 'Dashboard'
    require_login = True

    def dispatch(self, request, *args, **kwargs):
        if getattr(self, 'require_login', True):
            client_id = request.session.get('client_id')
            if not client_id:
                return redirect(reverse_lazy('client-login'))
        return super().dispatch(request, *args, **kwargs)

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


class LoginForm(forms.Form):
    phone = forms.CharField(max_length=20)
    password = forms.CharField(widget=forms.PasswordInput)


class LoginView(FormView):
    template_name = 'client/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('client-dashboard')
    require_login = False

    def form_valid(self, form):
        phone = form.cleaned_data['phone']
        password = form.cleaned_data['password']
        try:
            client = Client.objects.get(phone=phone)
        except Client.DoesNotExist:
            messages.error(self.request, 'Client not found')
            return redirect(reverse_lazy('client-login'))

        auth, _ = ClientAuth.objects.get_or_create(client=client)
        if auth.check_password(password):
            self.request.session['client_id'] = str(client.id)
            return super().form_valid(form)
        messages.error(self.request, 'Invalid credentials')
        return redirect(reverse_lazy('client-login'))


class SetPasswordForm(forms.Form):
    phone = forms.CharField(max_length=20)
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)


class SetPasswordView(FormView):
    template_name = 'client/set_password.html'
    form_class = SetPasswordForm
    success_url = reverse_lazy('client-login')
    require_login = False

    def form_valid(self, form):
        phone = form.cleaned_data['phone']
        password = form.cleaned_data['password']
        password_confirm = form.cleaned_data['password_confirm']
        if password != password_confirm:
            messages.error(self.request, 'Passwords do not match')
            return redirect(reverse_lazy('client-set-password'))
        client = get_object_or_404(Client, phone=phone)
        auth, _ = ClientAuth.objects.get_or_create(client=client)
        auth.set_password(password)
        messages.success(self.request, 'Password set. Please login.')
        return super().form_valid(form)


def logout_view(request):
    request.session.pop('client_id', None)
    return redirect(reverse_lazy('client-login'))


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer


class WalletBalanceView(generics.RetrieveAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletBalanceSerializer
    