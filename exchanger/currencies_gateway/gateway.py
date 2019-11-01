import grpc
import typing
from collections import OrderedDict
from django.conf import settings
from exchanger.gateway.base import BaseGateway
from exchanger.rpc.currencies_pb2_grpc import currencies__pb2 as currencies_pb2
from exchanger.rpc import currencies_pb2_grpc
from .serializers import CurrencySerializer
from .exceptions import CurrenciesBadResponseException


class CurrenciesServiceGateway(BaseGateway):
    """Hold logic for interacting with remote currencies service."""

    GW_ADDRESS = settings.CURRENCY_GW_ADDRESS
    MODULE = currencies_pb2
    TIMEOUT = settings.GRPC_TIMEOUT
    ServiceStub = currencies_pb2_grpc.CurrenciesServiceStub
    EXC_CLASS = CurrenciesBadResponseException
    NAME = 'currencies'
    ALLOWED_STATUTES = (currencies_pb2.SUCCESS, )
    BAD_RESPONSE_MSG = 'Bad response from currencies service'

    def get_currencies(self) -> typing.List[OrderedDict]:
        request_message = self.MODULE.CurrenciesRequest()
        with grpc.insecure_channel(self.GW_ADDRESS) as channel:
            stub = self.ServiceStub(channel)

            response = self._base_request(request_message, stub.Get)

        serializer = CurrencySerializer(data=response['currencies'], many=True)
        serializer.is_valid(raise_exception=True)
        return serializer.data
