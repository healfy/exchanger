import grpc
import typing
from django.conf import settings
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

    def put_on_monitoring(self,
                          wallet_id: int,
                          wallet_address: str,
                          expected_currency: str,
                          expected_address: str,
                          expected_amount: str,
                          uuid: str) -> typing.Union[dict, typing.Any]:
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
