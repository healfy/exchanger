import grpc
import logging
from datetime import datetime
from concurrent import futures
from contextlib import contextmanager
from django.conf import settings
from google.protobuf.json_format import MessageToDict
from .base import BaseRepr
from .serializers import TransactionDataSerializer
from exchanger.utils import nested_commit_on_success
from exchanger.models import OutPutTransaction
from exchanger.models import InputTransaction
from exchanger.rpc import exchanger_pb2_grpc
from exchanger.rpc.exchanger_pb2_grpc import exchanger__pb2 as exchanger_pb2

logger = logging.getLogger('exchanger')


class UpdateMixin:

    input_model = InputTransaction
    output_model = OutPutTransaction
    message = exchanger_pb2.UpdateResponse()
    serializer = TransactionDataSerializer

    @nested_commit_on_success
    def action(self, data, ingoing=False):
        model = self.input_model if ingoing else self.output_model
        counter = 0
        for trx in data:
            counter += model.objects.filter(uuid=trx['uuid'],
                                            status__in=model.ACTIVE_STATUTES
                                            ).update(
                trx_hash=trx['trx_hash'],
                value=trx['value'],
                confirmed_at=datetime.now(),
                status=model.CONFIRMED
            )
        self.message.header.status = exchanger_pb2.SUCCESS
        self.message.header.description = f'Updated  {counter} ' \
                                          f'of {model.__name__} objects'

    def validate_request(self, request):
        return self._validate(request)

    def _validate(self, request):
        request = MessageToDict(request, preserving_proto_field_name=True)
        serializer = self.serializer(data=request)
        serializer.is_valid(raise_exception=True)
        return serializer.data['transactions']

    def process(self, request, ingoing=False):
        try:
            self._execute(request, ingoing=ingoing)
        except Exception as e:
            logger.error(f'{self.__class__.__name__} got exception {e}')
            self.message.header.status = exchanger_pb2.ERROR
            self.message.header.description = f'{e}'
        return self.message

    def _execute(self, request, ingoing=False):
        data = self.validate_request(request)
        self.action(data, ingoing=ingoing)
        self.update_exchanger_objects(data, ingoing=ingoing)

    def update_exchanger_objects(self, data, ingoing=False):
        model = self.input_model if ingoing else self.output_model
        for trx in data:
            t = model.objects.filter(uuid=trx['uuid']).first()
            if t:
                t.exchange_history.request_update()


class ExchangerService(exchanger_pb2_grpc.ExchangerServiceServicer,
                       UpdateMixin,
                       BaseRepr):

    def Healthz(self, request, context):
        message = exchanger_pb2.HealthzResponse()
        message.header.status = exchanger_pb2.SUCCESS
        return message

    def UpdateInputTransaction(self, request, context):
        return self.process(request, ingoing=True)

    def UpdateOutputTransaction(self, request, context):
        return self.process(request)


@contextmanager
def serve_forever():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    exchanger_pb2_grpc.add_ExchangerServiceServicer_to_server(
        ExchangerService(), server)
    server.add_insecure_port(f'[::]:{settings.GRPC_SERVER_PORT}')
    server.start()
    logger.info(f'started GRPC server on port :{settings.GRPC_SERVER_PORT}')
    yield
    server.stop(0)
