from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from bank.models import Client, ClientAuth, Wallet
from deposits.models import Deposit
from paiement.models import Bill, Payment, ServiceProvider
from transfer.models import Transfer


class ClientLoginTests(TestCase):
    def test_login_uses_client_name_and_redirects_to_dashboard(self):
        client = Client.objects.create(name='Alice', phone='123456789', age=30, adress='Paris')
        auth = ClientAuth.objects.create(client=client)
        auth.set_password('secret123')

        response = self.client.post(reverse('client-login'), {
            'action': 'login',
            'name': 'Alice',
            'password': 'secret123',
        }, follow=True)

        self.assertRedirects(response, reverse('client-dashboard-by-id', args=[client.id]))
        self.assertTemplateUsed(response, 'client/client.html')
        self.assertEqual(self.client.session['client_id'], str(client.id))
        self.assertTrue(self.client.session.get_expire_at_browser_close())

    def test_login_sets_session_to_expire_on_browser_close(self):
        client = Client.objects.create(name='Bob', phone='987654321', age=26, adress='Lyon')
        auth = ClientAuth.objects.create(client=client)
        auth.set_password('password456')

        response = self.client.post(reverse('client-login'), {
            'action': 'login',
            'name': 'Bob',
            'password': 'password456',
        }, follow=True)

        self.assertRedirects(response, reverse('client-dashboard-by-id', args=[client.id]))
        self.assertTrue(self.client.session.get_expire_at_browser_close())

    def test_login_page_shows_signup_form_before_dashboard_access(self):
        response = self.client.get(reverse('client-login'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create your account')
        self.assertContains(response, 'name="action" value="signup"')
        self.assertContains(response, 'name="name"')

    def test_create_wallet_route_adds_wallet_for_logged_in_client(self):
        client = Client.objects.create(name='Bob', phone='987654321', age=26, adress='Lyon')
        auth = ClientAuth.objects.create(client=client)
        auth.set_password('password456')

        session = self.client.session
        session['client_id'] = str(client.id)
        session.save()

        self.assertEqual(Wallet.objects.filter(client=client).count(), 0)
        response = self.client.post(reverse('create-wallet'), follow=True)

        self.assertRedirects(response, reverse('client-dashboard-by-id', args=[client.id]))
        self.assertEqual(Wallet.objects.filter(client=client).count(), 1)

    def test_create_wallet_uses_the_client_from_the_active_page_not_shared_session(self):
        owner = Client.objects.create(name='Dana', phone='777777777', age=38, adress='Lille')
        other = Client.objects.create(name='Evan', phone='888888888', age=41, adress='Toulouse')

        session = self.client.session
        session['client_id'] = str(other.id)
        session.save()

        response = self.client.post(reverse('create-wallet'), {
            'client_id': str(owner.id),
            'currency': 'USD',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Wallet.objects.filter(client=owner).count(), 1)
        self.assertEqual(Wallet.objects.filter(client=other).count(), 0)

    def test_client_payment_page_only_shows_bills_assigned_to_that_client(self):
        owner = Client.objects.create(name='Alice', phone='111111111', age=30, adress='Paris')
        other = Client.objects.create(name='Bob', phone='222222222', age=31, adress='Lyon')
        provider = ServiceProvider.objects.create(name='Electricity', category='ELECTRICITY')
        Bill.objects.create(client=owner, provider=provider, reference_number='REF-001', amount_due='100.00')
        Bill.objects.create(client=other, provider=provider, reference_number='REF-002', amount_due='250.00')

        session = self.client.session
        session['client_id'] = str(owner.id)
        session.save()

        response = self.client.get(reverse('client-payment'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'REF-001')
        self.assertNotContains(response, 'REF-002')

    def test_client_payment_page_only_shows_providers_for_their_bills(self):
        owner = Client.objects.create(name='Alice', phone='111111111', age=30, adress='Paris')
        provider_with_bill = ServiceProvider.objects.create(name='Electricity', category='ELECTRICITY')
        provider_without_bill = ServiceProvider.objects.create(name='Internet', category='INTERNET')
        Bill.objects.create(client=owner, provider=provider_with_bill, reference_number='REF-001', amount_due='100.00')

        session = self.client.session
        session['client_id'] = str(owner.id)
        session.save()

        response = self.client.get(reverse('client-payment'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Electricity')
        self.assertNotContains(response, 'Internet')

    def test_client_cannot_submit_payment_for_another_clients_bill(self):
        owner = Client.objects.create(name='Alice', phone='111111111', age=30, adress='Paris')
        other = Client.objects.create(name='Bob', phone='222222222', age=31, adress='Lyon')
        provider = ServiceProvider.objects.create(name='Electricity', category='ELECTRICITY')
        bill = Bill.objects.create(client=other, provider=provider, reference_number='REF-002', amount_due='250.00')
        wallet = Wallet.objects.create(client=owner, balance=500.00, currency='USD')

        session = self.client.session
        session['client_id'] = str(owner.id)
        session.save()

        response = self.client.post(reverse('client-payment'), {
            'provider': provider.id,
            'bill': bill.id,
            'amount': '250.00'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('bill', response.context['payment_form'].errors)

    def test_bill_currency_is_saved_for_admin_reporting(self):
        owner = Client.objects.create(name='Alice', phone='333333333', age=30, adress='Paris')
        provider = ServiceProvider.objects.create(name='Water', category='WATER')

        bill = Bill.objects.create(
            client=owner,
            provider=provider,
            reference_number='REF-003',
            amount_due='75.50',
            currency='EUR',
        )

        self.assertEqual(bill.currency, 'EUR')
        self.assertIn('EUR', str(bill))

    def test_bill_remaining_amount_is_calculated_from_payments(self):
        owner = Client.objects.create(name='Alice', phone='444444444', age=32, adress='Paris')
        provider = ServiceProvider.objects.create(name='Internet', category='INTERNET')
        bill = Bill.objects.create(client=owner, provider=provider, reference_number='REF-004', amount_due='100.00')

        Payment.objects.create(bill=bill, wallet=Wallet.objects.create(client=owner, balance=1000.00, currency='USD'), amount='40.00')

        self.assertEqual(bill.remaining_amount, 60.00)

    def test_client_payment_page_displays_remaining_amount_to_pay(self):
        owner = Client.objects.create(name='Alice', phone='555555555', age=34, adress='Paris')
        provider = ServiceProvider.objects.create(name='Electricity', category='ELECTRICITY')
        Bill.objects.create(client=owner, provider=provider, reference_number='REF-005', amount_due='100.00')

        session = self.client.session
        session['client_id'] = str(owner.id)
        session.save()

        response = self.client.get(reverse('client-payment'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Remaining to pay')
        self.assertContains(response, '100.00')

    def test_client_dashboard_shows_pending_approvals_and_admin_link(self):
        owner = Client.objects.create(name='Charlie', phone='666666666', age=35, adress='Marseille')
        wallet = Wallet.objects.create(client=owner, balance=Decimal('50.00'), currency='USD')
        Deposit.objects.create(wallet=wallet, amount=Decimal('20.00'), channel='CASH')

        response = self.client.get(reverse('client-dashboard-by-id', args=[owner.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pending approval')
        self.assertContains(response, '/admin/')

    def test_client_dashboard_groups_total_balance_by_currency(self):
        owner = Client.objects.create(name='Faiza', phone='101010101', age=39, adress='Paris')
        Wallet.objects.create(client=owner, balance=Decimal('100.00'), currency='USD')
        Wallet.objects.create(client=owner, balance=Decimal('50.00'), currency='USD')
        Wallet.objects.create(client=owner, balance=Decimal('80.00'), currency='EUR')

        response = self.client.get(reverse('client-dashboard-by-id', args=[owner.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_balance'], Decimal('230.00'))
        self.assertIn('currency_totals', response.context)
        self.assertEqual(list(response.context['currency_totals']), [
            {'currency': 'EUR', 'total': Decimal('80.00')},
            {'currency': 'USD', 'total': Decimal('150.00')},
        ])

    def test_admin_portal_accepts_deposit_and_transfer_approval_actions(self):
        owner = Client.objects.create(name='Diana', phone='777777777', age=40, adress='Lyon')
        source_wallet = Wallet.objects.create(client=owner, balance=Decimal('100.00'), currency='USD')
        destination_wallet = Wallet.objects.create(client=owner, balance=Decimal('20.00'), currency='USD')
        deposit = Deposit.objects.create(wallet=source_wallet, amount=Decimal('30.00'), channel='BANK_TRANSFER')
        transfer = Transfer.objects.create(source_wallet=source_wallet, destination_wallet=destination_wallet, amount=Decimal('15.00'))

        session = self.client.session
        session['admin_authenticated'] = True
        session.save()

        response = self.client.post(reverse('admin-portal'), {
            'action': 'confirm_deposit',
            'deposit_id': deposit.id,
        })
        self.assertEqual(response.status_code, 200)
        deposit.refresh_from_db()
        self.assertTrue(deposit.is_confirmed)

        response = self.client.post(reverse('admin-portal'), {
            'action': 'authorize_transfer',
            'transfer_id': transfer.id,
        })
        self.assertEqual(response.status_code, 200)
        transfer.refresh_from_db()
        self.assertTrue(transfer.is_confirmed)
