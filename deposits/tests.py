from decimal import Decimal

from django.contrib.admin.sites import site
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase
from django.urls import reverse

from bank.models import Client, Wallet
from .admin import DepositAdmin
from .models import Deposit


class DepositConfirmationTests(TestCase):
    def test_deposit_is_created_pending_admin_confirmation(self):
        client = Client.objects.create(name='Alice', phone='111111111', age=30, adress='Paris')
        wallet = Wallet.objects.create(client=client, balance=Decimal('50.00'), currency='USD')

        response = self.client.post(
            reverse('deposit-list-create'),
            data={
                'wallet': wallet.id,
                'amount': '25.00',
                'channel': 'MOBILE_MONEY',
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        deposit = Deposit.objects.get(pk=response.json()['id'])
        self.assertFalse(deposit.is_confirmed)
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal('50.00'))

    def test_confirming_deposit_increases_wallet_balance(self):
        client = Client.objects.create(name='Bob', phone='222222222', age=31, adress='Lyon')
        wallet = Wallet.objects.create(client=client, balance=Decimal('10.00'), currency='USD')
        deposit = Deposit.objects.create(wallet=wallet, amount=Decimal('20.00'), channel='CASH')

        deposit.confirm()

        wallet.refresh_from_db()
        self.assertTrue(deposit.is_confirmed)
        self.assertEqual(wallet.balance, Decimal('30.00'))

    def test_admin_action_confirms_pending_deposits(self):
        client = Client.objects.create(name='Cara', phone='333333333', age=29, adress='Marseille')
        wallet = Wallet.objects.create(client=client, balance=Decimal('15.00'), currency='USD')
        deposit = Deposit.objects.create(wallet=wallet, amount=Decimal('5.00'), channel='CASH')

        request = RequestFactory().post('/admin/')
        setattr(request, 'session', {})
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        modeladmin = DepositAdmin(Deposit, site)
        modeladmin.confirm_selected(request, Deposit.objects.filter(pk=deposit.pk))

        deposit.refresh_from_db()
        self.assertTrue(deposit.is_confirmed)
        self.assertEqual(len(messages), 1)
