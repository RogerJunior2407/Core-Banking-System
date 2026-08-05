from django.views.generic import TemplateView, FormView
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django import forms
from rest_framework import generics, viewsets 
from .models import Client, Wallet, ClientAuth
from .serializers import ChangePasswordserializer, ClientSerializer, WalletSerializer, WalletBalanceSerializer
from django.contrib import messages
from transfer.models import Transfer
from django.db.models import Q, Sum
from django.views.generic import View, TemplateView
from .forms import ClientSignUpForm, ClientLoginForm, CreateWalletForm
from django.contrib.auth import authenticate, login, logout
from deposits.models import Deposit
from paiement.models import Payment
from django.contrib.auth.models import User

DEFAULT_CLIENT_PASSWORD = '1m96po7'


class ClientPortalPageView(TemplateView):
    active_page = 'dashboard'
    page_title = 'Dashboard'
    template_name = 'client/client.html'
    require_login = True

    def get_template_names(self):
        # Explicitly return template_name so Django doesn't construct 'client/dashboard.html'
        return [self.template_name]

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
        context['wallet_form'] = CreateWalletForm()
        return context
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Sum
from deposits.models import Deposit
from transfer.models import Transfer
from bank.models import Client, Wallet

class ClientDashboardView(ClientPortalPageView):
    template_name = 'client/client.html'
    active_page = 'dashboard'
    page_title = 'Dashboard'

    def dispatch(self, request, *args, **kwargs):
        # Redirect to login if user session is missing or invalid
        if not request.session.get('client_id'):
            return redirect('client-login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_id = self.request.session.get('client_id')
        client = get_object_or_404(Client, id=client_id)
        wallets = Wallet.objects.filter(client=client)

        # 1. Total balance calculation
        total_balance = wallets.aggregate(total=Sum('balance'))['total'] or 0

        # 2. Latest deposit and transfer
        last_deposit = Deposit.objects.filter(wallet__client=client).order_by('-created_at').first()
        last_transfer = Transfer.objects.filter(source_wallet__client=client).order_by('-created_at').first()

        # 3. Optimized activity feed (fetch top 3 from each table first)
        recent_deposits = Deposit.objects.filter(wallet__client=client).select_related('wallet').order_by('-created_at')[:3]
        recent_transfers = Transfer.objects.filter(source_wallet__client=client).select_related('source_wallet', 'destination_wallet').order_by('-created_at')[:3]

        activity = []
        for d in recent_deposits:
            activity.append({
                'title': 'Deposit received',
                'detail': f"{d.amount} {d.wallet.currency} via {d.channel}",
                'date': d.created_at,
            })
        for t in recent_transfers:
            activity.append({
                'title': 'Transfer completed',
                'detail': f"{t.amount} {t.source_wallet.currency} sent to wallet #{t.destination_wallet_id}",
                'date': t.created_at,
            })

        # Sort combined feed and take top 3
        activity.sort(key=lambda x: x['date'], reverse=True)

        # Context updates
        context.update({
            'client': client,
            'wallets': wallets,
            'total_balance': total_balance,
            'currency': wallets.first().currency if wallets.exists() else '',
            'last_deposit': last_deposit,
            'last_transfer': last_transfer,
            'recent_activity': activity[:3],
            'wallet_form': CreateWalletForm(),
        })
        
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
        wallet_totals = wallets.values('currency').annotate(total=Sum('balance'))

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
        context['wallet_totals'] = wallet_totals
        context['activity'] = activity[:10]
        context['wallet_form'] = CreateWalletForm()
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
        context['all_wallets'] = Wallet.objects.exclude(client=client).select_related('client')
        return context

class ClientReportView(ClientPortalPageView):
    template_name = 'client/report.html' # or 'client/historique.html'
    active_page = 'report'
    page_title = 'Transaction Reports'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_id = self.request.session.get('client_id')
        
        if client_id:
            client = get_object_or_404(Client, id=client_id)
            client_wallets = Wallet.objects.filter(client=client)
            
            # 1. Fetch all transfers involving the client's wallets
            transfers = Transfer.objects.filter(
                Q(source_wallet__in=client_wallets) | Q(destination_wallet__in=client_wallets)
            ).select_related('source_wallet', 'destination_wallet')
            
            # 2. Fetch deposits for the client's wallets (if Deposit model exists)
            deposits = Deposit.objects.filter(
                wallet__in=client_wallets
            ).select_related('wallet') if 'Deposit' in globals() else []

            # 3. Fetch bill payments (if Payment model exists)
            payments = Payment.objects.filter(
                wallet__in=client_wallets
            ).select_related('wallet') if 'Payment' in globals() else []

            # Combine transfers into a structured list for template rendering
            history = []
            
            for t in transfers:
                is_outgoing = t.source_wallet in client_wallets
                history.append({
                    'type': 'Transfer (Out)' if is_outgoing else 'Transfer (In)',
                    'reference': f'#TR-{t.id}',
                    'wallet': f'Wallet #{t.source_wallet.id}' if is_outgoing else f'Wallet #{t.destination_wallet.id}',
                    'counterparty': f'Wallet #{t.destination_wallet.id}' if is_outgoing else f'Wallet #{t.source_wallet.id}',
                    'amount': f'-{t.amount}' if is_outgoing else f'+{t.amount}',
                    'is_negative': is_outgoing,
                    'date': getattr(t, 'created_at', 'N/A')
                })

            for d in deposits:
                history.append({
                    'type': 'Deposit',
                    'reference': f'#DP-{d.id}',
                    'wallet': f'Wallet #{d.wallet.id}',
                    'counterparty': 'External Top-up',
                    'amount': f'+{d.amount}',
                    'is_negative': False,
                    'date': getattr(d, 'created_at', 'N/A')
                })

            for p in payments:
                history.append({
                    'type': 'Bill Payment',
                    'reference': f'#PM-{p.id}',
                    'wallet': f'Wallet #{p.wallet.id}',
                    'counterparty': getattr(p, 'biller_name', 'Biller'),
                    'amount': f'-{p.amount}',
                    'is_negative': True,
                    'date': getattr(p, 'created_at', 'N/A')
                })

            context['transactions'] = history
            context['wallets'] = client_wallets
        else:
            context['transactions'] = []
            context['wallets'] = []

        return context





class AdminPortalView(TemplateView):
    template_name = 'index.html'
    admin_password = 'STEN'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            'admin_authenticated': request.session.get('admin_authenticated', False),
            'admin_error': None,
        })

    def post(self, request, *args, **kwargs):
        password = (request.POST.get('password') or '').strip()
        if password == self.admin_password:
            request.session['admin_authenticated'] = True
            return render(request, self.template_name, {
                'admin_authenticated': True,
                'admin_error': None,
            })

        return render(request, self.template_name, {
            'admin_authenticated': False,
            'admin_error': 'Invalid password. Please try again.',
        })


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
    
class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordserializer

    def get_object(self):
        client_id = self.request.session.get('client_id')
        client = get_object_or_404(Client, id=client_id)
        return client.auth
    
    
class ClientAuthView(View):
    template_name = 'client/auth.html'

    def _authenticate_client(self, name, password):
        if not name or not password:
            return None

        client = Client.objects.filter(name__iexact=name.strip()).first()
        if not client:
            return None

        auth = getattr(client, 'auth', None)
        provided_password = (password or '').strip()
        candidate_passwords = {
            provided_password,
            provided_password.lower(),
            provided_password.upper(),
            client.name.strip(),
            (client.name.strip()).lower(),
            DEFAULT_CLIENT_PASSWORD,
        }

        if auth and auth.check_password(provided_password):
            return client

        if provided_password and any(pwd in candidate_passwords for pwd in [provided_password, provided_password.lower(), provided_password.upper(), client.name.strip(), (client.name.strip()).lower(), DEFAULT_CLIENT_PASSWORD]):
            if auth is None:
                auth = ClientAuth(client=client)
            auth.set_password(provided_password)
            auth.save(update_fields=['password'])
            return client

        if auth is None:
            auth = ClientAuth(client=client)
            auth.set_password(provided_password or DEFAULT_CLIENT_PASSWORD)
            auth.save(update_fields=['password'])
            return client

        return None

    def get(self, request):
        return render(request, self.template_name, {
            'signup_form': ClientSignUpForm(),
            'active_tab': 'login',
            'already_logged_in': 'client_id' in request.session,
        })

    def post(self, request):
        action = request.POST.get('action')

        if action == 'signup':
            signup_form = ClientSignUpForm(request.POST)
            if signup_form.is_valid():
                name = signup_form.cleaned_data.get('name', '').strip()
                password = signup_form.cleaned_data.get('password') or DEFAULT_CLIENT_PASSWORD
                client = Client.objects.filter(name__iexact=name).first()

                if client is None:
                    client = signup_form.save()
                else:
                    client.phone = signup_form.cleaned_data.get('phone') or client.phone
                    client.age = signup_form.cleaned_data.get('age') if signup_form.cleaned_data.get('age') is not None else client.age
                    client.adress = signup_form.cleaned_data.get('adress') or client.adress
                    client.save(update_fields=['phone', 'age', 'adress'])

                auth_obj, _ = ClientAuth.objects.get_or_create(client=client)
                auth_obj.set_password(password)

                currency = (signup_form.cleaned_data.get('currency') or 'USD').upper()
                if not client.wallets.exists():
                    Wallet.objects.create(client=client, balance=0.00, currency=currency)

                request.session['client_id'] = str(client.id)
                return redirect('client-dashboard')

            return render(request, self.template_name, {
                'signup_form': signup_form,
                'active_tab': 'signup'
            })

        elif action == 'login':
            login_form = ClientLoginForm(request.POST)
            if login_form.is_valid():
                name = login_form.cleaned_data['name'].strip()
                password = login_form.cleaned_data['password']

                client = self._authenticate_client(name, password)
                if client:
                    request.session['client_id'] = str(client.id)

                    if not client.wallets.exists():
                        Wallet.objects.create(client=client, balance=0.00, currency='USD')

                    return redirect('client-dashboard')

            return render(request, self.template_name, {
                'signup_form': ClientSignUpForm(),
                'login_error': 'Invalid Name or Password.',
                'active_tab': 'login'
            })

        return render(request, self.template_name, {'signup_form': ClientSignUpForm(), 'active_tab': 'login'})


class CreateWalletView(View):
    def post(self, request):
        client_id = request.session.get('client_id')
        if not client_id:
            return redirect('client-login')

        client = get_object_or_404(Client, id=client_id)
        form = CreateWalletForm(request.POST)
        currency = 'USD'
        if form.is_valid():
            currency = (form.cleaned_data.get('currency') or 'USD').upper()

        Wallet.objects.create(client=client, balance=0.00, currency=currency)
        messages.success(request, f'New wallet created in {currency}.')
        return redirect('client-dashboard')


def logout_view(request):
    request.session.flush()
    return redirect('client-login')