from django.conf import settings
from django.core.management.base import BaseCommand
from exchanger.models import PlatformWallet, Currency


class Command(BaseCommand):
    help = 'create wallets and currencies'

    def handle(self, *args, **options):

        bitcoin = Currency.objects.get_create(
            name='Bitcoin',
            slug='bitcoin',
        )

        ethereum = Currency.objects.get_create(
            name='Ethereum',
            slug='ethereum',
        )
        
        Currency.objects.get_create(
            name='Omisego',
            slug='omisego',
            is_token=True,
        ),
        Currency.objects.get_create(
            name='Basic Attention Token',
            slug='basic-attention-token',
            is_token=True,
        ),
        Currency.objects.get_create(
            name='Holo',
            slug='holo',
            is_token=True,
        ),
        Currency.objects.get_create(
            name='Chainlink',
            slug='chainlink',
            is_token=True,
        ),
        Currency.objects.get_create(
            name='Zilliqa',
            slug='zilliqa',
            is_token=True,
        ),

        PlatformWallet.objects.get_or_create(
            address=settings.BTC_ADDRESS,
            currency=bitcoin,
            external_id=settings.BTC_EXTERNAL_ID

        )
        PlatformWallet.objects.get_or_create(
            address=settings.ETH_ADDRESS,
            currency=ethereum,
            external_id=settings.ETH_EXTERNAL_ID
        )
