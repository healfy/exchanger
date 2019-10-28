import grpc
from django.conf import settings
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE

from exchanger.gateway.base import BaseGateway
from exchanger.rpc.wallets_pb2_grpc import wallets__pb2 as wallets_pb2
from exchanger.rpc import wallets_pb2_grpc


class WalletsServiceGateway(BaseGateway):
    """Hold logic for interacting with remote wallets service."""

    GW_ADDRESS = settings.WALLETS_GW_ADDRESS
    MODULE = wallets_pb2
    ServiceStub = wallets_pb2_grpc.WalletsStub
    ALLOWED_STATUTES = (wallets_pb2.SUCCESS,)

    def put_on_monitoring(self,
                          external_id: int,
                          address: str,
                          currency_slug: str,
                          expected_address: str,
                          is_platform: bool = True) -> Response:
        """
        Method that send request to service wallet to start monitoring
        current wallet for incoming transactions
        :param external_id: wallet id from database
        :param address: wallet address from blockchain
        :param is_platform: feature by which wallets differ, default false
        :param currency_slug: currency slug of  wallet
        :param expected_address: address from we are expect transfer
        """

        request_message = self.MODULE.PlatformWLTMonitoringRequest(
            expected_address=expected_address
        )

        with grpc.insecure_channel(self.GW_ADDRESS) as channel:
            client = self.ServiceStub(channel)

            operation_success, result = self._base_request(
                request_message,
                client.StartMonitoringPlatformWallet,
            )
        if not operation_success:
            return Response(result, HTTP_503_SERVICE_UNAVAILABLE)

        return Response(result, HTTP_200_OK)
