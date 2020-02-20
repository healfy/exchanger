from django.test import TestCase
from uuid import uuid4
from django.conf import settings
from unittest.mock import patch
from exchanger.states import wallets_service_gw
from exchanger.rpc.transactions_pb2_grpc import \
    transactions__pb2 as transactions_pb2
from exchanger.models import (
    Currency,
    PlatformWallet,
    ExchangeHistory,
    TransactionBase
)
from rest_framework.test import APIClient
from exchanger import states


class TestBase(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        settings.TEST_MODE = True
        bitcoin, _ = Currency.objects.get_or_create(
            name='Bitcoin',
            slug='bitcoin',
        )

        ethereum, _ = Currency.objects.get_or_create(
            name='Ethereum',
            slug='ethereum',
        )

        Currency.objects.get_or_create(
            name='Omisego',
            slug='omisego',
            is_token=True,
        ),
        Currency.objects.get_or_create(
            name='Basic Attention Token',
            slug='basic-attention-token',
            is_token=True,
        )
        self.token_in, _ = Currency.objects.get_or_create(
            name='Holo',
            slug='holo',
            is_token=True,
        )
        self.token_out, _ = Currency.objects.get_or_create(
            name='Chainlink',
            slug='chainlink',
            is_token=True,
        )
        Currency.objects.get_or_create(
            name='Zilliqa',
            slug='zilliqa',
            is_token=True,
        )

        self.btc_wallet, _ = PlatformWallet.objects.get_or_create(
            address='test_bitcoin_address',
            currency=bitcoin,
            external_id=1

        )
        self.eth_wallet, _ = PlatformWallet.objects.get_or_create(
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
            self.assertEqual(obj.from_currency.slug, self.data['from_currency'])
            self.assertEqual(obj.to_currency.slug, self.data['to_currency'])

    def get_obj(self, resp):
        obj = ExchangeHistory.objects.filter(uuid=resp.json()['uuid'])
        self.assertIsNotNone(obj)
        return obj.get()

    def test_create_exchanger_bitcoin(self, *args):
        self.data.update({
            'from_currency': self.btc_wallet.currency.slug,
            'to_currency': self.btc_wallet.currency.slug,
            'ingoing_amount': '1',
            'outgoing_amount': '0.92',
        })
        resp = self.client.post('/api/exchange/', data=self.data)
        self.assertEqual(201, resp.status_code)
        obj = self.get_obj(resp)
        self.assertEqual(obj.ingoing_wallet, self.btc_wallet)
        self.assertEqual(obj.outgoing_wallet, self.btc_wallet)
        self.inspect_obj(obj)

        self.assertEqual(obj.state, states.WaitingHashState)
        self.assertEqual(obj.fee, settings.DEFAULT_FEE)

    def test_create_exchanger_ethereum(self, *args):
        self.data.update({
            'from_currency': self.eth_wallet.currency.slug,
            'to_currency': self.eth_wallet.currency.slug,
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
        self.assertEqual(obj.state, states.WaitingHashState)
        self.assertEqual(obj.fee, settings.EXTENDED_FEE)

 #   @patch.object(wallets_service_gw, '_base_request', return_value={})
    def test_create_exchanger_token_1(self, *args):
        self.data.update({
            'from_currency': self.token_in.slug,
            'to_currency': self.eth_wallet.currency.slug,
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
        self.assertEqual(obj.state, states.WaitingHashState)
        self.assertEqual(obj.fee, settings.EXTENDED_FEE)

    def test_create_exchanger_token_2(self, *args):
        self.data.update({
            'from_currency': self.token_in.slug,
            'to_currency': self.token_out.slug,
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
        self.assertEqual(obj.state, states.WaitingHashState)
        self.assertEqual(obj.fee, settings.EXTENDED_FEE)

    def test_invalid_email_cases_1(self):
        exc_test = ['This field may not be blank.']
        self.data.update({
            'user_email': '',
            'from_currency': self.eth_wallet.currency.slug,
            'to_currency': self.eth_wallet.currency.slug,
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
            'from_currency': self.eth_wallet.currency.slug,
            'to_currency': self.eth_wallet.currency.slug,
            'ingoing_amount': '10',
            'outgoing_amount': '9.81',
        })
        resp = self.client.post('/api/exchange/', data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['user_email'], exc_test)

    def test_invalid_from_currency_case_1(self):
        exc_text = ['This field is required.']

        self.data.update({
            'to_currency': self.eth_wallet.currency.slug,
            'ingoing_amount': '10',
            'outgoing_amount': '9.81'
        })
        resp = self.client.post('/api/exchange/', data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['from_currency'], exc_text)

    def test_invalid_from_currency_case_2(self):
        exc_text = ['Currency matching query does not exist.']

        self.data.update({
            'to_currency': self.eth_wallet.currency.slug,
            'from_currency': 'tether',
            'ingoing_amount': '10',
            'outgoing_amount': '9.81'
        })
        resp = self.client.post('/api/exchange/', data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['from_currency'], exc_text)

    def test_invalid_to_currency_case_1(self):
        exc_text = ['This field is required.']

        self.data.update({
            'from_currency': self.eth_wallet.currency.slug,
            'ingoing_amount': '10',
            'outgoing_amount': '9.81'
        })
        resp = self.client.post('/api/exchange/', data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['to_currency'], exc_text)

    def test_invalid_to_currency_case_2(self):
        exc_text = ['Currency matching query does not exist.']

        self.data.update({
            'from_currency': self.eth_wallet.currency.slug,
            'to_currency': 'random_slug',
            'ingoing_amount': '10',
            'outgoing_amount': '9.81'
        })
        resp = self.client.post('/api/exchange/', data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['to_currency'], exc_text)

    def test_invalid_outgoing_amount(self):
        amount = 0
        exc_text = [f'Invalid outgoing amount 0.0']
        self.data.update({
            'from_currency': self.eth_wallet.currency.slug,
            'to_currency': self.eth_wallet.currency.slug,
            'ingoing_amount': '10',
            'outgoing_amount': amount,
        })
        resp = self.client.post('/api/exchange/', data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['outgoing_amount'], exc_text)

    def test_invalid_ingoing_amount(self):
        amount = 0
        exc_text = [f'Invalid ingoing amount 0.0']
        self.data.update({
            'from_currency': self.eth_wallet.currency.slug,
            'to_currency': self.eth_wallet.currency.slug,
            'ingoing_amount': amount,
            'outgoing_amount': '2.21',
        })
        resp = self.client.post('/api/exchange/', data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['ingoing_amount'], exc_text)


class TestStates(TestBase):

    def setUp(self) -> None:
        super().setUp()
        self.email = 'test_email@mail.ru'
        self.to_address = uuid4()
        self.from_address = uuid4()
        data = {
            'from_currency': self.btc_wallet.currency,
            'to_currency': self.btc_wallet.currency,
            'ingoing_amount': '1',
            'outgoing_amount': '0.92',
            'user_email': self.email,
            'from_address': str(self.from_address),
            'to_address': str(self.to_address),
            'fee': settings.DEFAULT_FEE,
        }

        self.exchanger = ExchangeHistory.objects.create(**data)

    def update_obj(self, count):
        for i in range(count):
            self.exchanger.request_update()
        self.exchanger.refresh_from_db()

    def test_unknown_state(self):
        self.assertEqual(self.exchanger.state, states.UnknownState)
        self.assertIsNone(self.exchanger.outgoing_wallet)
        self.assertIsNone(self.exchanger.ingoing_wallet)
        self.assertIsNone(self.exchanger.transaction_input)
        self.assertIsNone(self.exchanger.transaction_output)

    def test_issued_state(self):
        self.exchanger.request_update(stop_status=ExchangeHistory.NEW)
        self.exchanger.refresh_from_db()
        self.assertEqual(self.exchanger.state, states.NewState)
        self.assertIsNotNone(self.exchanger.outgoing_wallet)
        self.assertIsNotNone(self.exchanger.ingoing_wallet)

    @patch.object(wallets_service_gw, '_base_request', return_value={})
    def test_waiting_hash_state(self, *args):
        self.exchanger.request_update(stop_status=ExchangeHistory.WAITING_HASH)
        self.exchanger.refresh_from_db()
        self.assertEqual(self.exchanger.state, states.WaitingHashState)
        self.assertIsNone(self.exchanger.transaction_input.trx_hash)
        _hash = str(uuid4())
        resp = self.client.post(
            f'/api/exchange/{self.exchanger.uuid}/update_transaction/',
            data={'trx_hash': _hash})
        self.assertEqual(200,  resp.status_code)
        self.exchanger.refresh_from_db()
        self.assertEqual(self.exchanger.transaction_input.trx_hash, _hash)

    @patch.object(wallets_service_gw, '_base_request', return_value={})
    def test_waiting_deposit_state(self, *args):
        self.exchanger.request_update(stop_status=ExchangeHistory.WAITING_HASH)
        self.exchanger.refresh_from_db()
        self.assertEqual(self.exchanger.state, states.WaitingHashState)
        self.assertIsNone(self.exchanger.transaction_input.trx_hash)
        _hash = str(uuid4())
        self.client.post(
            f'/api/exchange/{self.exchanger.uuid}/update_transaction/',
            data={'trx_hash': _hash})
        self.exchanger.refresh_from_db()
        self.assertEqual(self.exchanger.state, states.WaitingDepositState)
        self.assertEqual(self.exchanger.transaction_input.trx_hash, _hash)
        trx = self.exchanger.transaction_input
        self.assertEqual(trx.from_address, self.exchanger.from_address)
        self.assertEqual(trx.to_address, self.exchanger.ingoing_wallet.address)
        self.assertEqual(trx.currency, self.exchanger.from_currency)

    @patch.object(wallets_service_gw, '_base_request', return_value={})
    @patch.object(states.WaitingDepositState, 'validate_value',
                  return_value=True)
    def test_deposit_payed_state(self, *args):
        self.update_obj(2)
        self.exchanger.status = ExchangeHistory.WAITING_DEPOSIT
        self.exchanger.save()
        self.exchanger.refresh_from_db()
        trx = self.exchanger.transaction_input
        trx.trx_hash = uuid4()
        trx.status = TransactionBase.CONFIRMED
        trx.save()
        self.exchanger.request_update(stop_status=ExchangeHistory.DEPOSIT_PAID)
        self.exchanger.refresh_from_db()
        self.assertEqual(self.exchanger.state, states.DepositPaidState)

    @patch.object(wallets_service_gw, '_base_request', return_value={})
    @patch.object(states.WaitingDepositState, 'validate_value',
                  return_value=True)
    def test_calculating_state(self, *args):
        self.update_obj(2)
        self.exchanger.status = ExchangeHistory.DEPOSIT_PAID
        self.exchanger.save()
        self.exchanger.refresh_from_db()
        trx = self.exchanger.transaction_input
        trx.trx_hash = uuid4()
        trx.status = TransactionBase.CONFIRMED
        trx.save()
        self.exchanger.request_update(stop_status=ExchangeHistory.CALCULATING)
        self.exchanger.refresh_from_db()
        self.assertEqual(self.exchanger.state, states.CalculatingState)

    @patch.object(wallets_service_gw, '_base_request', return_value={})
    @patch.object(states.WaitingDepositState, 'validate_value',
                  return_value=True)
    def test_create_outgoing_state(self, *args):
        self.update_obj(2)
        self.exchanger.status = ExchangeHistory.CALCULATING
        self.exchanger.save()
        self.exchanger.refresh_from_db()
        trx = self.exchanger.transaction_input
        trx.trx_hash = uuid4()
        trx.status = TransactionBase.CONFIRMED
        trx.save()
        self.exchanger.request_update(
            stop_status=ExchangeHistory.CREATING_OUTGOING_TRANSFER)
        self.exchanger.refresh_from_db()
        self.assertEqual(self.exchanger.state, states.CreatingOutGoingState)
        trx_out = self.exchanger.transaction_output
        self.assertEqual(trx_out.to_address, self.exchanger.to_address)
        self.assertEqual(trx_out.value, self.exchanger.outgoing_amount)
        self.assertEqual(trx_out.currency, self.exchanger.to_currency)

    @patch.object(wallets_service_gw, '_base_request', return_value={})
    @patch.object(states.CreatingOutGoingState.gw, '_base_request',
                  return_value={"header": {"status": transactions_pb2.SUCCESS}})
    @patch.object(states.WaitingDepositState, 'validate_value',
                  return_value=True)
    def test_outgoing_running_state(self, *args):
        self.update_obj(2)
        self.exchanger.status = ExchangeHistory.DEPOSIT_PAID
        self.exchanger.save()
        self.exchanger.refresh_from_db()
        trx = self.exchanger.transaction_input
        trx.trx_hash = uuid4()
        trx.status = TransactionBase.CONFIRMED
        trx.save()
        self.exchanger.request_update()
        self.exchanger.request_update()
        self.exchanger.refresh_from_db()
        self.assertEqual(self.exchanger.state, states.OutgoingRunningState)

    @patch.object(wallets_service_gw, '_base_request', return_value={})
    @patch.object(states.CreatingOutGoingState.gw, '_base_request',
                  return_value={"header": {"status": transactions_pb2.ERROR}})
    @patch.object(states.WaitingDepositState, 'validate_value',
                  return_value=True)
    def test_failed_creating_transfer(self, *args):
        self.update_obj(2)
        self.exchanger.status = ExchangeHistory.DEPOSIT_PAID
        self.exchanger.save()
        self.exchanger.refresh_from_db()
        trx = self.exchanger.transaction_input
        trx.trx_hash = uuid4()
        trx.status = TransactionBase.CONFIRMED
        trx.save()
        self.exchanger.request_update(
            stop_status=ExchangeHistory.CREATING_OUTGOING_TRANSFER)
        self.exchanger.refresh_from_db()
        self.exchanger.request_update(
            stop_status=ExchangeHistory.OUTGOING_RUNNING)
        self.assertEqual(self.exchanger.state, states.CreatingOutGoingState)

    @patch.object(wallets_service_gw, '_base_request', return_value={})
    @patch.object(states.CreatingOutGoingState.gw, 'create_transfer',
                  return_value={"header": {"status": transactions_pb2.SUCCESS}})
    @patch.object(states.WaitingDepositState, 'validate_value',
                  return_value=True)
    def test_closed_state(self, *args):
        self.update_obj(2)
        self.exchanger.status = ExchangeHistory.DEPOSIT_PAID
        self.exchanger.save()
        self.exchanger.refresh_from_db()
        trx = self.exchanger.transaction_input
        trx.trx_hash = uuid4()
        trx.status = TransactionBase.CONFIRMED
        trx.save()
        self.exchanger.request_update(
            stop_status=ExchangeHistory.CREATING_OUTGOING_TRANSFER)
        self.exchanger.refresh_from_db()
        trx_out = self.exchanger.transaction_output
        trx_out.trx_hash = uuid4()
        trx_out.status = TransactionBase.CONFIRMED
        trx_out.save()
        self.exchanger.request_update(
            stop_status=ExchangeHistory.CLOSED)
        self.exchanger.refresh_from_db()
        self.assertEqual(self.exchanger.state, states.ClosedState)

    @patch.object(wallets_service_gw, '_base_request', return_value={})
    @patch.object(states.WaitingDepositState, 'validate_value',
                  return_value=False)
    def test_insufficient_state(self, *args):
        self.update_obj(2)
        self.exchanger.status = ExchangeHistory.WAITING_DEPOSIT
        self.exchanger.save()
        self.exchanger.refresh_from_db()
        trx = self.exchanger.transaction_input
        trx.trx_hash = uuid4()
        trx.status = TransactionBase.CONFIRMED
        trx.save()
        self.exchanger.request_update(
            stop_status=ExchangeHistory.INSUFFICIENT_DEPOSIT)
        self.exchanger.refresh_from_db()
        self.assertEqual(self.exchanger.state, states.InsufficientDepositState)

    @patch.object(wallets_service_gw, '_base_request', return_value={})
    @patch.object(states.WaitingDepositState, 'validate_value',
                  return_value=False)
    @patch.object(states.CreatingOutGoingState.gw, 'create_transfer',
                  return_value={"header": {"status": transactions_pb2.SUCCESS}})
    def test_returning_deposit_state(self, *args):
        self.update_obj(2)
        self.exchanger.status = ExchangeHistory.WAITING_DEPOSIT
        self.exchanger.save()
        self.exchanger.refresh_from_db()
        trx = self.exchanger.transaction_input
        trx.trx_hash = uuid4()
        trx.status = TransactionBase.CONFIRMED
        trx.save()
        self.exchanger.request_update(
            stop_status=ExchangeHistory.RETURNING_DEPOSIT)
        self.exchanger.refresh_from_db()
        self.assertEqual(self.exchanger.state, states.ReturningDepositState)

    @patch.object(wallets_service_gw, '_base_request', return_value={})
    @patch.object(states.WaitingDepositState, 'validate_value',
                  return_value=False)
    @patch.object(states.CreatingOutGoingState.gw, 'create_transfer',
                  return_value={"header": {"status": transactions_pb2.ERROR}})
    def test_returning_deposit_state_failed(self, *args):
        self.update_obj(2)
        self.exchanger.status = ExchangeHistory.WAITING_DEPOSIT
        self.exchanger.save()
        self.exchanger.refresh_from_db()
        trx = self.exchanger.transaction_input
        trx.trx_hash = uuid4()
        trx.status = TransactionBase.CONFIRMED
        trx.save()
        self.exchanger.request_update(
            stop_status=ExchangeHistory.RETURNING_DEPOSIT)
        self.exchanger.refresh_from_db()
        self.assertEqual(self.exchanger.state, states.InsufficientDepositState)

    @patch.object(wallets_service_gw, '_base_request', return_value={})
    @patch.object(states.WaitingDepositState, 'validate_value',
                  return_value=False)
    @patch.object(states.CreatingOutGoingState.gw, 'create_transfer',
                  return_value={"header":{"status": transactions_pb2.SUCCESS}})
    def test_failed_state(self, *args):
        self.update_obj(2)
        self.exchanger.status = ExchangeHistory.WAITING_DEPOSIT
        self.exchanger.save()
        self.exchanger.refresh_from_db()
        trx = self.exchanger.transaction_input
        trx.trx_hash = uuid4()
        trx.status = TransactionBase.CONFIRMED
        trx.save()
        self.exchanger.request_update(
            stop_status=ExchangeHistory.RETURNING_DEPOSIT)
        self.exchanger.refresh_from_db()
        trx_out = self.exchanger.transaction_output
        trx_out.trx_hash = uuid4()
        trx_out.status = TransactionBase.CONFIRMED
        trx_out.save()
        self.exchanger.request_update(
            stop_status=ExchangeHistory.FAILED)
        self.exchanger.refresh_from_db()
        self.assertEqual(self.exchanger.state, states.FailedState)
