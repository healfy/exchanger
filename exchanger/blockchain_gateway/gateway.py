import grpc
import typing
from django.conf import settings
from exchanger.gateway.base import BaseGateway
from exchanger.models import InputTransaction
from exchanger.rpc.blockchain_gateway_pb2_grpc import \
    blockchain__gateway__pb2 as blockchain_gateway_pb2
from exchanger.rpc import blockchain_gateway_pb2_grpc
from .exceptions import BlockchainBadResponseException
from .serializers import BGWTransactionSerializer


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
            self,
            address: str = None,
            currency_slug: str = None
    ) -> typing.Dict:
        """
        Function to validate addresses which were entered by the user

        :param address: current address
        :param currency_slug: currency of address
        """

        request_message = self.MODULE.CheckAddressRequest(
            address=address,
            currencySlug=currency_slug)

        with grpc.insecure_channel(self.GW_ADDRESS) as channel:
            client = self.ServiceStub(channel)
            response_data = self._base_request(request_message,
                                               client.CheckAddress)
            response_data['isinstance'] = response_data.get('isinstance', False)
        return response_data

    def get_transaction(
            self,
            _hash: str,
            currency_slug: str,
            to_address,
            instance: InputTransaction
    ) -> BGWTransactionSerializer:
        """

        :param _hash: hash of current transaction
        :param currency_slug: currency of current transaction
        :param to_address: target address of current transaction
        :param instance: InputTransaction linked with exchanger object and
        current transaction
        """
        request_message = self.MODULE.GetTransactionRequest(
            hash=_hash, currencySlug=currency_slug, to=to_address
        )
        with grpc.insecure_channel(self.GW_ADDRESS) as channel:
            client = self.ServiceStub(channel)
            response_data = self._base_request(
                request_message, client.GetTransaction,
                extend_statutes=(blockchain_gateway_pb2.PENDING,
                                 blockchain_gateway_pb2.NOT_FOUND))

            data = response_data['transaction']
            data['status'] = response_data[self.response_attr]['status']

            serializer = BGWTransactionSerializer(data=data, instance=instance)

        return serializer
