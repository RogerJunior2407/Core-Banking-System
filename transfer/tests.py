from decimal import Decimal

from django.contrib.admin.sites import site
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase

from bank.models import Client, Wallet
from .admin import TransferAdmin
from .models import Transfer


class TransferAuthorizationTests(TestCase):
    def test_admin_action_authorizes_pending_transfers(self):
        source_client = Client.objects.create(name='Dina', phone='444444444', age=35, adress='Nice')
        destination_client = Client.objects.create(name='Eli', phone='555555555', age=40, adress='Bordeaux')
        source_wallet = Wallet.objects.create(client=source_client, balance=Decimal('100.00'), currency='USD')
        destination_wallet = Wallet.objects.create(client=destination_client, balance=Decimal('10.00'), currency='USD')
        transfer = Transfer.objects.create(
            source_wallet=source_wallet,
            destination_wallet=destination_wallet,
            amount=Decimal('25.00'),
        )

        request = RequestFactory().post('/admin/')
        setattr(request, 'session', {})
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        modeladmin = TransferAdmin(Transfer, site)
        modeladmin.authorize_selected(request, Transfer.objects.filter(pk=transfer.pk))

        transfer.refresh_from_db()
        source_wallet.refresh_from_db()
        destination_wallet.refresh_from_db()

        self.assertTrue(transfer.is_confirmed)
        self.assertEqual(source_wallet.balance, Decimal('75.00'))
        self.assertEqual(destination_wallet.balance, Decimal('35.00'))
        self.assertEqual(len(messages), 1)

    def test_transfer_creation_requires_matching_client_context(self):
        source_client = Client.objects.create(name='Fiona', phone='888888888', age=37, adress='Reims')
        destination_client = Client.objects.create(name='Gabe', phone='999999999', age=42, adress='Montpellier')
        source_wallet = Wallet.objects.create(client=source_client, balance=Decimal('100.00'), currency='USD')
        destination_wallet = Wallet.objects.create(client=destination_client, balance=Decimal('10.00'), currency='USD')

        response = self.client.post(
            '/transfer/',
            data={
                'source_wallet': source_wallet.id,
                'destination_wallet': destination_wallet.id,
                'amount': '25.00',
                'client_id': str(destination_client.id),
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('client_id', response.json())
