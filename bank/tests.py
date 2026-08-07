from django.test import TestCase
from django.urls import reverse

from bank.models import Client, ClientAuth, Wallet
from paiement.models import Bill, ServiceProvider


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

        self.assertRedirects(response, reverse('client-dashboard'))
        self.assertTemplateUsed(response, 'client/client.html')
        self.assertEqual(self.client.session['client_id'], str(client.id))

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

        self.assertRedirects(response, reverse('client-dashboard'))
        self.assertEqual(Wallet.objects.filter(client=client).count(), 1)

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
