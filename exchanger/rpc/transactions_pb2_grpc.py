# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import transactions_pb2 as transactions__pb2


class TransactionsStub(object):
  """TransactionsService server
  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.Healthz = channel.unary_unary(
        '/transaction.Transactions/Healthz',
        request_serializer=transactions__pb2.HealthzRequest.SerializeToString,
        response_deserializer=transactions__pb2.HealthzResponse.FromString,
        )
    self.CreateTransfer = channel.unary_unary(
        '/transaction.Transactions/CreateTransfer',
        request_serializer=transactions__pb2.CreateTransferRequest.SerializeToString,
        response_deserializer=transactions__pb2.CreateTransferResponse.FromString,
        )
    self.StartMonitoring = channel.unary_unary(
        '/transaction.Transactions/StartMonitoring',
        request_serializer=transactions__pb2.StartMonitoringRequest.SerializeToString,
        response_deserializer=transactions__pb2.StartMonitoringResponse.FromString,
        )
    self.GetOutPutTransactions = channel.unary_unary(
        '/transaction.Transactions/GetOutPutTransactions',
        request_serializer=transactions__pb2.GetOutPutRequest.SerializeToString,
        response_deserializer=transactions__pb2.GetOutPutResponse.FromString,
        )


class TransactionsServicer(object):
  """TransactionsService server
  """

  def Healthz(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def CreateTransfer(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def StartMonitoring(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetOutPutTransactions(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_TransactionsServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'Healthz': grpc.unary_unary_rpc_method_handler(
          servicer.Healthz,
          request_deserializer=transactions__pb2.HealthzRequest.FromString,
          response_serializer=transactions__pb2.HealthzResponse.SerializeToString,
      ),
      'CreateTransfer': grpc.unary_unary_rpc_method_handler(
          servicer.CreateTransfer,
          request_deserializer=transactions__pb2.CreateTransferRequest.FromString,
          response_serializer=transactions__pb2.CreateTransferResponse.SerializeToString,
      ),
      'StartMonitoring': grpc.unary_unary_rpc_method_handler(
          servicer.StartMonitoring,
          request_deserializer=transactions__pb2.StartMonitoringRequest.FromString,
          response_serializer=transactions__pb2.StartMonitoringResponse.SerializeToString,
      ),
      'GetOutPutTransactions': grpc.unary_unary_rpc_method_handler(
          servicer.GetOutPutTransactions,
          request_deserializer=transactions__pb2.GetOutPutRequest.FromString,
          response_serializer=transactions__pb2.GetOutPutResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'transaction.Transactions', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
