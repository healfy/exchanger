import grpc
import typing
from decimal import Decimal
from django.conf import settings
from exchanger.gateway.base import BaseGateway
from exchanger.rpc.transactions_pb2_grpc import \
    transactions__pb2 as transactions_pb2
from exchanger.rpc import transactions_pb2_grpc
from .exceptions import TransactionsBadResponseException


class TransactionsServiceGateway(BaseGateway):
    """Hold logic for interacting with remote wallets service."""

    GW_ADDRESS = settings.TRANSACTIONS_GW_ADDRESS
    MODULE = transactions_pb2
    NAME = 'transactions'
    ServiceStub = transactions_pb2_grpc.TransactionsStub
    ALLOWED_STATUTES = (transactions_pb2.SUCCESS,)
    EXC_CLASS = TransactionsBadResponseException
    BAD_RESPONSE_MSG = 'Bad response from transactions gateway.'

    def create_transfer(
            self,
            address_from: str = None,
            address_to: str = None,
            currency_slug: str = None,
            value: typing.Union[str, Decimal] = None,
            wallet_id: int = None,
            uuid: str = None
    ) -> typing.Union[dict, typing.Any]:

        request_message = self.MODULE.CreateTransferRequest(
            transfer=transactions_pb2.Transfer(
                address_from=address_from,
                address_to=address_to,
                currencySlug=currency_slug,
                value=str(value),
                wallet_id=wallet_id,
                uuid=str(uuid)),
        )

        with grpc.insecure_channel(self.GW_ADDRESS) as channel:
            client = self.ServiceStub(channel)

            resp = self._base_request(
                request_message,
                client.CreateTransfer,
            )
        return resp
