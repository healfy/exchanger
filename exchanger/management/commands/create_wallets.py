from django.conf import settings
from django.core.management.base import BaseCommand
from exchanger.models import PlatformWallet, Currency


class Command(BaseCommand):
    help = 'create wallets'

    def handle(self, *args, **options):
        bitcoin = Currency.objects.create(
            name='bitcoin',
            slug='bitcoin',
        )
        ethereum = Currency.objects.create(
            name='ethereum',
            slug='ethereum',
        )

        PlatformWallet.objects.create(
            address='2N8xEvNfrAPrHcGYzbj2iWkPEQEBbhhPXaD',
            currency=bitcoin

        )
        PlatformWallet.objects.create(
            address='0xe9e93D36F1182f6658b41f7a7A4Fa241e7aee691',
            currency=ethereum
        )
