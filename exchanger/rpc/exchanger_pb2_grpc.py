# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import exchanger_pb2 as exchanger__pb2


class ExchangerServiceStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.Healthz = channel.unary_unary(
        '/exchanger.ExchangerService/Healthz',
        request_serializer=exchanger__pb2.HealthzRequest.SerializeToString,
        response_deserializer=exchanger__pb2.HealthzResponse.FromString,
        )


class ExchangerServiceServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def Healthz(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_ExchangerServiceServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'Healthz': grpc.unary_unary_rpc_method_handler(
          servicer.Healthz,
          request_deserializer=exchanger__pb2.HealthzRequest.FromString,
          response_serializer=exchanger__pb2.HealthzResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'exchanger.ExchangerService', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))