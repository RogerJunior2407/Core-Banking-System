from django.core.management.base import BaseCommand
from bank.models import Client, ClientAuth


class Command(BaseCommand):
    help = 'Set password for all existing clients (create ClientAuth entries if missing)'

    def add_arguments(self, parser):
        parser.add_argument('--password', type=str, default='1m96po7', help='Password to set for all clients')

    def handle(self, *args, **options):
        pwd = options['password']
        clients = Client.objects.all()
        count = 0
        for client in clients:
            auth, created = ClientAuth.objects.get_or_create(client=client)
            auth.set_password(pwd)
            count += 1
        self.stdout.write(self.style.SUCCESS(f'Set password for {count} clients'))
