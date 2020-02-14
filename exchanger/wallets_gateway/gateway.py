import grpc
import typing
from decimal import Decimal
from django.conf import settings
from exchanger.utils import all_kwargs_required
from exchanger.gateway.base import BaseGateway
from exchanger.rpc.wallets_pb2_grpc import wallets__pb2 as wallets_pb2
from exchanger.rpc import wallets_pb2_grpc
from .exceptions import WalletsBadResponseException


class WalletsServiceGateway(BaseGateway):
    """Hold logic for interacting with remote wallets service."""

    GW_ADDRESS = settings.WALLETS_GW_ADDRESS
    MODULE = wallets_pb2
    NAME = 'wallets'
    ServiceStub = wallets_pb2_grpc.WalletsStub
    ALLOWED_STATUTES = (wallets_pb2.SUCCESS,)
    EXC_CLASS = WalletsBadResponseException
    BAD_RESPONSE_MSG = 'Bad response from wallets gateway.'

    @all_kwargs_required
    def put_on_monitoring(
            self,
            *,
            wallet_id: int = None,
            wallet_address: str = None,
            expected_currency: str = None,
            expected_address: str = None,
            expected_amount: str = None,
            uuid: str = None
    ) -> typing.Union[dict, typing.Any]:
        """
        Method that send request to service wallet to start monitoring
        current wallet for incoming transaction from expected_address
        :param wallet_id: wallet id from database
        :param wallet_address: wallet address from blockchain
        :param expected_amount: amount of transaction
        :param expected_currency: currency slug of  transaction
        :param expected_address: address from we are expect transfer
        :param uuid: unique internal identifier for transactions

        """

        request_message = self.MODULE.PlatformWLTMonitoringRequest(
            expected_address=expected_address,
            wallet_id=wallet_id,
            wallet_address=wallet_address,
            expected_currency=expected_currency,
            expected_amount=str(expected_amount),
            uuid=str(uuid),
        )

        with grpc.insecure_channel(self.GW_ADDRESS) as channel:
            client = self.ServiceStub(channel)

            resp = self._base_request(
                request_message,
                client.StartMonitoringPlatformWallet,
            )
        return resp

    @all_kwargs_required
    def add_input_transaction(
            self,
            *,
            trx_hash: str = None,
            wallet_address: str = None,
            currency_slug: str = None,
            from_address: str = None,
            amount: Decimal = None,
            uuid: str = None
    ):
        """
        Method that send request to service wallet to start monitoring
        current transaction from user address
        :param trx_hash: hash of trx from database
        :param wallet_address: exchanger wallet address from blockchain
        :param currency_slug: currency slug of  transaction
        :param from_address: user wallet address
        :param amount: amount of transaction
        :param uuid: unique internal identifier for transactions
        """
        request_message = self.MODULE.InputTransactionRequest(
            from_address=from_address,
            hash=trx_hash,
            wallet_address=wallet_address,
            currency=currency_slug,
            value=str(amount),
            uuid=str(uuid),
        )

        with grpc.insecure_channel(self.GW_ADDRESS) as channel:
            client = self.ServiceStub(channel)

            resp = self._base_request(
                request_message,
                client.AddInputTransaction,
            )
        return resp
