import grpc
import logging
from concurrent import futures
from contextlib import contextmanager
from exchanger.rpc import exchanger_pb2_grpc

logger = logging.getLogger('exchanger')


class ExchangerService(exchanger_pb2_grpc.ExchangerServiceServicer):

    def Healthz(self, request, context):
        pass


@contextmanager
def serve_forever():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    exchanger_pb2_grpc.add_ExchangerServiceServicer_to_server(
        ExchangerService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info('started GRPC server on port :50051')
    yield
    server.stop(0)
