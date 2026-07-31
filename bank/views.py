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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_id = self.request.session.get('client_id')
        client = get_object_or_404(Client, id=client_id)
        wallets = Wallet.objects.filter(client=client)

        from deposits.models import Deposit
        from transfer.models import Transfer
        from django.db.models import Sum

        # Solde total (toutes devises confondues, additionnées brut)
        total_balance = wallets.aggregate(total=Sum('balance'))['total'] or 0

        # Dernier dépôt
        last_deposit = Deposit.objects.filter(wallet__client=client).order_by('-created_at').first()

        # Dernier transfert envoyé (le plus récent, sert de "transfert en attente/récent")
        last_transfer = Transfer.objects.filter(source_wallet__client=client).order_by('-created_at').first()

        # Activité récente combinée (dépôts + transferts), les 3 dernières
        activity = []
        for d in Deposit.objects.filter(wallet__client=client).select_related('wallet'):
            activity.append({
                'title': 'Deposit received',
                'detail': f"{d.amount} {d.wallet.currency} via {d.channel}",
                'date': d.created_at,
            })
        for t in Transfer.objects.filter(source_wallet__client=client).select_related('source_wallet', 'destination_wallet'):
            activity.append({
                'title': 'Transfer completed',
                'detail': f"{t.amount} {t.source_wallet.currency} sent to wallet #{t.destination_wallet_id}",
                'date': t.created_at,
            })

        activity.sort(key=lambda x: x['date'], reverse=True)

        context['total_balance'] = total_balance
        context['currency'] = wallets.first().currency if wallets.exists() else ''
        context['last_deposit'] = last_deposit
        context['last_transfer'] = last_transfer
        context['recent_activity'] = activity[:3]
        return context


class ClientWalletView(ClientPortalPageView):
    template_name = 'client/wallet.html'
    active_page = 'wallet'
    page_title = 'Wallet'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_id = self.request.session.get('client_id')
        client = get_object_or_404(Client, id=client_id)
        wallets = Wallet.objects.filter(client=client)

        # Historique combiné : dépôts + transferts
        from deposits.models import Deposit
        from transfer.models import Transfer

        deposits = Deposit.objects.filter(wallet__client=client).select_related('wallet')
        transfers = (
            Transfer.objects.filter(source_wallet__client=client)
            | Transfer.objects.filter(destination_wallet__client=client)
        ).distinct().select_related('source_wallet', 'destination_wallet')

        activity = []
        for d in deposits:
            activity.append({
                'date': d.created_at,
                'wallet': d.wallet.currency,
                'type': 'Deposit',
                'amount': d.amount,
                'sign': '+',
            })
        for t in transfers:
            is_source = t.source_wallet.client_id == client.id
            activity.append({
                'date': t.created_at,
                'wallet': t.source_wallet.currency if is_source else t.destination_wallet.currency,
                'type': 'Transfer',
                'amount': t.amount,
                'sign': '-' if is_source else '+',
            })

        activity.sort(key=lambda x: x['date'], reverse=True)

        context['wallets'] = wallets
        context['activity'] = activity[:10]
        return context


class ClientDepositView(ClientPortalPageView):
    template_name = 'client/deposit.html'
    active_page = 'deposit'
    page_title = 'Deposit'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_id = self.request.session.get('client_id')
        client = get_object_or_404(Client, id=client_id)
        context['wallets'] = Wallet.objects.filter(client=client)
        return context



class ClientTransferView(ClientPortalPageView):
    template_name = 'client/transfer.html'
    active_page = 'transfer'
    page_title = 'Transfer'
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_id = self.request.session.get('client_id')
        client = get_object_or_404(Client, id=client_id)
        context['wallets'] = Wallet.objects.filter(client=client)
        return context
 
    def post(self, request, *args, **kwargs):
        from decimal import Decimal, InvalidOperation
        from transfer.models import Transfer
 
        client_id = request.session.get('client_id')
        client = get_object_or_404(Client, id=client_id)
 
        source_wallet_id = request.POST.get('source_wallet')
        recipient_phone = request.POST.get('recipient_phone')
        amount_raw = request.POST.get('amount')
 
        source_wallet = get_object_or_404(Wallet, id=source_wallet_id, client=client)
 
        # Validation du montant
        try:
            amount = Decimal(amount_raw)
        except (TypeError, InvalidOperation):
            messages.error(request, 'Invalid amount.')
            return redirect(reverse_lazy('client-transfer'))
 
        if amount <= 0:
            messages.error(request, 'Amount must be greater than zero.')
            return redirect(reverse_lazy('client-transfer'))
 
        # Recherche du destinataire par téléphone
        try:
            recipient_client = Client.objects.get(phone=recipient_phone)
        except Client.DoesNotExist:
            messages.error(request, 'No client found with that phone number.')
            return redirect(reverse_lazy('client-transfer'))
 
        if recipient_client.id == client.id:
            messages.error(request, 'You cannot transfer to your own account.')
            return redirect(reverse_lazy('client-transfer'))
 
        destination_wallet = Wallet.objects.filter(
            client=recipient_client, currency=source_wallet.currency
        ).first()
        if destination_wallet is None:
            messages.error(request, f'Recipient has no {source_wallet.currency} wallet.')
            return redirect(reverse_lazy('client-transfer'))
 
        with transaction.atomic():
            # Verrouillage des deux portefeuilles pour éviter les conditions de concurrence
            source = Wallet.objects.select_for_update().get(pk=source_wallet.pk)
            destination = Wallet.objects.select_for_update().get(pk=destination_wallet.pk)
 
            if source.balance < amount:
                messages.error(request, 'Insufficient balance in source wallet.')
                return redirect(reverse_lazy('client-transfer'))
 
            source.balance -= amount
            destination.balance += amount
            source.save(update_fields=['balance'])
            destination.save(update_fields=['balance'])
 
            Transfer.objects.create(
                source_wallet=source,
                destination_wallet=destination,
                amount=amount,
            )
 
        messages.success(request, f'Transfer of {amount} {source.currency} sent successfully.')
        return redirect(reverse_lazy('client-transfer'))

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
    