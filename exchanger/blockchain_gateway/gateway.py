import grpc
import typing
from django.conf import settings
from exchanger.gateway.base import BaseGateway
from exchanger.rpc.blockchain_gateway_pb2_grpc import \
    blockchain__gateway__pb2 as blockchain_gateway_pb2
from exchanger.rpc import blockchain_gateway_pb2_grpc
from .exceptions import BlockchainBadResponseException


class BlockChainServiceGateway(BaseGateway):
    """Hold logic for interacting with remote wallets service."""

    GW_ADDRESS = settings.BLOCKCHAIN_GW_ADDRESS
    MODULE = blockchain_gateway_pb2
    NAME = 'bgw'
    ServiceStub = blockchain_gateway_pb2_grpc.BlockchainGatewayServiceStub
    ALLOWED_STATUTES = (blockchain_gateway_pb2.SUCCESS,)
    EXC_CLASS = BlockchainBadResponseException
    BAD_RESPONSE_MSG = 'Bad response from blockchain gateway.'
    response_attr: str = 'status'

    def check_address(
            self, address: str = None,
            currency_slug: str = None
    ) -> typing.Dict:

        request_message = self.MODULE.CheckAddressRequest(
            address=address,
            currencySlug=currency_slug)

        with grpc.insecure_channel(self.GW_ADDRESS) as channel:
            client = self.ServiceStub(channel)
            response_data = self._base_request(request_message,
                                               client.CheckAddress)
            response_data['isinstance'] = response_data.get('isinstance', False)
        return response_data
