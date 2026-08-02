from django.test import TestCase
from django.urls import reverse

from bank.models import Client, ClientAuth, Wallet


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
