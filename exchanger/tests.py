from django.test import TestCase
from uuid import uuid4

from django.conf import settings
from unittest.mock import patch
from exchanger.states import wallets_service_gw

from exchanger.models import Currency, PlatformWallet, ExchangeHistory
from rest_framework.test import APIClient
from exchanger import states


class TestBase(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        settings.TEST_MODE = True
        bitcoin = Currency.objects.create(
            name='Bitcoin',
            slug='bitcoin',
        )

        ethereum = Currency.objects.create(
            name='Ethereum',
            slug='ethereum',
        )

        Currency.objects.create(
            name='Omisego',
            slug='omisego',
            is_token=True,
        ),
        Currency.objects.create(
            name='Basic Attention Token',
            slug='basic-attention-token',
            is_token=True,
        )
        self.token_in = Currency.objects.create(
            name='Holo',
            slug='holo',
            is_token=True,
        )
        self.token_out = Currency.objects.create(
            name='Chainlink',
            slug='chainlink',
            is_token=True,
        )
        Currency.objects.create(
            name='Zilliqa',
            slug='zilliqa',
            is_token=True,
        )

        self.btc_wallet = PlatformWallet.objects.create(
            address='test_bitcoin_address',
            currency=bitcoin,
            external_id=1

        )
        self.eth_wallet = PlatformWallet.objects.create(
            address='test_etherium_address',
            currency=ethereum,
            external_id=2
        )


class TestSettingsApi(TestCase):
    """
    Test Cases for Exchanger Service API
    """

    def test_settings(self):
        data = {
            'default': settings.DEFAULT_FEE,
            'extended': settings.EXTENDED_FEE,
            'limit': settings.MIN_FEE_LIMIT
        }
        response = self.client.get('/api/settings/')
        self.assertEqual(200, response.status_code)
        self.assertEqual(data, response.json())


class TestExchangerApi(TestBase):
    attrs = {
        'from_currency_id': 'from_currency',
        'to_currency_id': 'to_currency',
        'from_address': 'from_address',
        'to_address': 'to_address',
    }

    def setUp(self) -> None:
        super().setUp()
        self.email = 'test_email@mail.ru'
        self.to_address = uuid4()
        self.from_address = uuid4()
        self.data = {
            'user_email': self.email,
            'from_address': str(self.from_address),
            'to_address': str(self.to_address),
            'fee': settings.DEFAULT_FEE,
        }

    def inspect_obj(self, obj):
        for key, value in self.attrs.items():
            self.assertEqual(getattr(obj, key), self.data[value])

    def get_obj(self, resp):
        obj = ExchangeHistory.objects.filter(id=resp.json()['id'])
        self.assertIsNotNone(obj)
        return obj.get()

    @patch.object(wallets_service_gw, '_base_request', return_value={})
    def test_create_exchanger_bitcoin(self, *args):
        self.data.update({
            'from_currency': self.btc_wallet.currency.id,
            'to_currency': self.btc_wallet.currency.id,
            'ingoing_amount': '1',
            'outgoing_amount': '0.92',
        })
        resp = self.client.post('/api/exchange/', data=self.data)
        self.assertEqual(201, resp.status_code)
        obj = self.get_obj(resp)
        self.assertEqual(obj.ingoing_wallet, self.btc_wallet)
        self.assertEqual(obj.outgoing_wallet, self.btc_wallet)
        self.inspect_obj(obj)

        self.assertEqual(obj.state, states.WaitingDepositState)
        self.assertEqual(obj.fee, settings.DEFAULT_FEE)

    @patch.object(wallets_service_gw, '_base_request', return_value={})
    def test_create_exchanger_ethereum(self, *args):
        self.data.update({
            'from_currency': self.eth_wallet.currency.id,
            'to_currency': self.eth_wallet.currency.id,
            'ingoing_amount': '10',
            'outgoing_amount': '9.81',
            'fee': settings.EXTENDED_FEE,
        })
        resp = self.client.post('/api/exchange/', data=self.data)
        self.assertEqual(201, resp.status_code)
        obj = self.get_obj(resp)
        self.inspect_obj(obj)
        self.assertEqual(obj.ingoing_wallet, self.eth_wallet)
        self.assertEqual(obj.outgoing_wallet, self.eth_wallet)
        self.assertEqual(obj.state, states.WaitingDepositState)
        self.assertEqual(obj.fee, settings.EXTENDED_FEE)

    @patch.object(wallets_service_gw, '_base_request', return_value={})
    def test_create_exchanger_token_1(self, *args):
        self.data.update({
            'from_currency': self.token_in.id,
            'to_currency': self.eth_wallet.currency.id,
            'ingoing_amount': '10',
            'outgoing_amount': '9.81',
            'fee': settings.EXTENDED_FEE,
        })
        resp = self.client.post('/api/exchange/', data=self.data)
        self.assertEqual(201, resp.status_code)
        obj = self.get_obj(resp)
        self.inspect_obj(obj)
        self.assertEqual(obj.ingoing_wallet, self.eth_wallet)
        self.assertEqual(obj.outgoing_wallet, self.eth_wallet)
        self.assertEqual(obj.state, states.WaitingDepositState)
        self.assertEqual(obj.fee, settings.EXTENDED_FEE)

    @patch.object(wallets_service_gw, '_base_request', return_value={})
    def test_create_exchanger_token_2(self, *args):
        self.data.update({
            'from_currency': self.token_in.id,
            'to_currency': self.token_out.id,
            'ingoing_amount': '10',
            'outgoing_amount': '9.81',
            'fee': settings.EXTENDED_FEE,
        })
        resp = self.client.post('/api/exchange/', data=self.data)
        self.assertEqual(201, resp.status_code)
        obj = self.get_obj(resp)
        self.inspect_obj(obj)
        self.assertEqual(obj.ingoing_wallet, self.eth_wallet)
        self.assertEqual(obj.outgoing_wallet, self.eth_wallet)
        self.assertEqual(obj.state, states.WaitingDepositState)
        self.assertEqual(obj.fee, settings.EXTENDED_FEE)

    def test_invalid_email_cases_1(self):
        exc_test = ['This field may not be blank.']
        self.data.update({
            'user_email': '',
            'from_currency': self.eth_wallet.currency.id,
            'to_currency': self.eth_wallet.currency.id,
            'ingoing_amount': '10',
            'outgoing_amount': '9.81',
        })
        resp = self.client.post('/api/exchange/', data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['user_email'], exc_test)


    def test_invalid_email_cases_2(self):
        exc_test = ['Enter a valid email address.']
        self.data.update({
            'user_email': '123123123',
            'from_currency': self.eth_wallet.currency.id,
            'to_currency': self.eth_wallet.currency.id,
            'ingoing_amount': '10',
            'outgoing_amount': '9.81',
        })
        resp = self.client.post('/api/exchange/', data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['user_email'], exc_test)

