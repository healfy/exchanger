# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: exchanger.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from google.protobuf import duration_pb2 as google_dot_protobuf_dot_duration__pb2
from google.api import annotations_pb2 as google_dot_api_dot_annotations__pb2
from protoc_gen_swagger.options import annotations_pb2 as protoc__gen__swagger_dot_options_dot_annotations__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='exchanger.proto',
  package='exchanger',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x0f\x65xchanger.proto\x12\texchanger\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1egoogle/protobuf/duration.proto\x1a\x1cgoogle/api/annotations.proto\x1a,protoc-gen-swagger/options/annotations.proto\"P\n\x0eResponseHeader\x12)\n\x06status\x18\x01 \x01(\x0e\x32\x19.exchanger.ResponseStatus\x12\x13\n\x0b\x64\x65scription\x18\x02 \x01(\t\"\x10\n\x0eHealthzRequest\"<\n\x0fHealthzResponse\x12)\n\x06header\x18\x01 \x01(\x0b\x32\x19.exchanger.ResponseHeader\"P\n\x0fTransactionData\x12\x0c\n\x04uuid\x18\x01 \x01(\t\x12\x10\n\x08trx_hash\x18\x02 \x01(\t\x12\r\n\x05value\x18\x03 \x01(\t\x12\x0e\n\x06status\x18\x04 \x01(\x03\"A\n\rUpdateRequest\x12\x30\n\x0ctransactions\x18\x01 \x03(\x0b\x32\x1a.exchanger.TransactionData\";\n\x0eUpdateResponse\x12)\n\x06header\x18\x01 \x01(\x0b\x32\x19.exchanger.ResponseHeader*\xe4\x01\n\x10\x45xchangeStatutes\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x07\n\x03NEW\x10\x01\x12\x13\n\x0fWAITING_DEPOSIT\x10\x02\x12\x18\n\x14INSUFFICIENT_DEPOSIT\x10\x03\x12\x10\n\x0c\x44\x45POSIT_PAID\x10\x04\x12\x1e\n\x1a\x43REATING_OUTGOING_TRANSFER\x10\x05\x12\x14\n\x10OUTGOING_RUNNING\x10\x06\x12\n\n\x06\x43LOSED\x10\x07\x12\n\n\x06\x46\x41ILED\x10\x08\x12\x15\n\x11RETURNING_DEPOSIT\x10\t\x12\x14\n\x10\x44\x45POSIT_RETURNED\x10\n*J\n\x0eResponseStatus\x12\x0b\n\x07NOT_SET\x10\x00\x12\x0b\n\x07SUCCESS\x10\x01\x12\t\n\x05\x45RROR\x10\x02\x12\x13\n\x0fINVALID_REQUEST\x10\x03\x32\xf9\x01\n\x10\x45xchangerService\x12\x42\n\x07Healthz\x12\x19.exchanger.HealthzRequest\x1a\x1a.exchanger.HealthzResponse\"\x00\x12O\n\x16UpdateInputTransaction\x12\x18.exchanger.UpdateRequest\x1a\x19.exchanger.UpdateResponse\"\x00\x12P\n\x17UpdateOutputTransaction\x12\x18.exchanger.UpdateRequest\x1a\x19.exchanger.UpdateResponse\"\x00\x62\x06proto3')
  ,
  dependencies=[google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR,google_dot_protobuf_dot_duration__pb2.DESCRIPTOR,google_dot_api_dot_annotations__pb2.DESCRIPTOR,protoc__gen__swagger_dot_options_dot_annotations__pb2.DESCRIPTOR,])

_EXCHANGESTATUTES = _descriptor.EnumDescriptor(
  name='ExchangeStatutes',
  full_name='exchanger.ExchangeStatutes',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='UNKNOWN', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='NEW', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='WAITING_DEPOSIT', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='INSUFFICIENT_DEPOSIT', index=3, number=3,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DEPOSIT_PAID', index=4, number=4,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CREATING_OUTGOING_TRANSFER', index=5, number=5,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='OUTGOING_RUNNING', index=6, number=6,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CLOSED', index=7, number=7,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='FAILED', index=8, number=8,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='RETURNING_DEPOSIT', index=9, number=9,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DEPOSIT_RETURNED', index=10, number=10,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=544,
  serialized_end=772,
)
_sym_db.RegisterEnumDescriptor(_EXCHANGESTATUTES)

ExchangeStatutes = enum_type_wrapper.EnumTypeWrapper(_EXCHANGESTATUTES)
_RESPONSESTATUS = _descriptor.EnumDescriptor(
  name='ResponseStatus',
  full_name='exchanger.ResponseStatus',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='NOT_SET', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SUCCESS', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ERROR', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='INVALID_REQUEST', index=3, number=3,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=774,
  serialized_end=848,
)
_sym_db.RegisterEnumDescriptor(_RESPONSESTATUS)

ResponseStatus = enum_type_wrapper.EnumTypeWrapper(_RESPONSESTATUS)
UNKNOWN = 0
NEW = 1
WAITING_DEPOSIT = 2
INSUFFICIENT_DEPOSIT = 3
DEPOSIT_PAID = 4
CREATING_OUTGOING_TRANSFER = 5
OUTGOING_RUNNING = 6
CLOSED = 7
FAILED = 8
RETURNING_DEPOSIT = 9
DEPOSIT_RETURNED = 10
NOT_SET = 0
SUCCESS = 1
ERROR = 2
INVALID_REQUEST = 3



_RESPONSEHEADER = _descriptor.Descriptor(
  name='ResponseHeader',
  full_name='exchanger.ResponseHeader',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='exchanger.ResponseHeader.status', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='description', full_name='exchanger.ResponseHeader.description', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=171,
  serialized_end=251,
)


_HEALTHZREQUEST = _descriptor.Descriptor(
  name='HealthzRequest',
  full_name='exchanger.HealthzRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=253,
  serialized_end=269,
)


_HEALTHZRESPONSE = _descriptor.Descriptor(
  name='HealthzResponse',
  full_name='exchanger.HealthzResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='header', full_name='exchanger.HealthzResponse.header', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=271,
  serialized_end=331,
)


_TRANSACTIONDATA = _descriptor.Descriptor(
  name='TransactionData',
  full_name='exchanger.TransactionData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='uuid', full_name='exchanger.TransactionData.uuid', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='trx_hash', full_name='exchanger.TransactionData.trx_hash', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='exchanger.TransactionData.value', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='status', full_name='exchanger.TransactionData.status', index=3,
      number=4, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=333,
  serialized_end=413,
)


_UPDATEREQUEST = _descriptor.Descriptor(
  name='UpdateRequest',
  full_name='exchanger.UpdateRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='transactions', full_name='exchanger.UpdateRequest.transactions', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=415,
  serialized_end=480,
)


_UPDATERESPONSE = _descriptor.Descriptor(
  name='UpdateResponse',
  full_name='exchanger.UpdateResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='header', full_name='exchanger.UpdateResponse.header', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=482,
  serialized_end=541,
)

_RESPONSEHEADER.fields_by_name['status'].enum_type = _RESPONSESTATUS
_HEALTHZRESPONSE.fields_by_name['header'].message_type = _RESPONSEHEADER
_UPDATEREQUEST.fields_by_name['transactions'].message_type = _TRANSACTIONDATA
_UPDATERESPONSE.fields_by_name['header'].message_type = _RESPONSEHEADER
DESCRIPTOR.message_types_by_name['ResponseHeader'] = _RESPONSEHEADER
DESCRIPTOR.message_types_by_name['HealthzRequest'] = _HEALTHZREQUEST
DESCRIPTOR.message_types_by_name['HealthzResponse'] = _HEALTHZRESPONSE
DESCRIPTOR.message_types_by_name['TransactionData'] = _TRANSACTIONDATA
DESCRIPTOR.message_types_by_name['UpdateRequest'] = _UPDATEREQUEST
DESCRIPTOR.message_types_by_name['UpdateResponse'] = _UPDATERESPONSE
DESCRIPTOR.enum_types_by_name['ExchangeStatutes'] = _EXCHANGESTATUTES
DESCRIPTOR.enum_types_by_name['ResponseStatus'] = _RESPONSESTATUS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ResponseHeader = _reflection.GeneratedProtocolMessageType('ResponseHeader', (_message.Message,), {
  'DESCRIPTOR' : _RESPONSEHEADER,
  '__module__' : 'exchanger_pb2'
  # @@protoc_insertion_point(class_scope:exchanger.ResponseHeader)
  })
_sym_db.RegisterMessage(ResponseHeader)

HealthzRequest = _reflection.GeneratedProtocolMessageType('HealthzRequest', (_message.Message,), {
  'DESCRIPTOR' : _HEALTHZREQUEST,
  '__module__' : 'exchanger_pb2'
  # @@protoc_insertion_point(class_scope:exchanger.HealthzRequest)
  })
_sym_db.RegisterMessage(HealthzRequest)

HealthzResponse = _reflection.GeneratedProtocolMessageType('HealthzResponse', (_message.Message,), {
  'DESCRIPTOR' : _HEALTHZRESPONSE,
  '__module__' : 'exchanger_pb2'
  # @@protoc_insertion_point(class_scope:exchanger.HealthzResponse)
  })
_sym_db.RegisterMessage(HealthzResponse)

TransactionData = _reflection.GeneratedProtocolMessageType('TransactionData', (_message.Message,), {
  'DESCRIPTOR' : _TRANSACTIONDATA,
  '__module__' : 'exchanger_pb2'
  # @@protoc_insertion_point(class_scope:exchanger.TransactionData)
  })
_sym_db.RegisterMessage(TransactionData)

UpdateRequest = _reflection.GeneratedProtocolMessageType('UpdateRequest', (_message.Message,), {
  'DESCRIPTOR' : _UPDATEREQUEST,
  '__module__' : 'exchanger_pb2'
  # @@protoc_insertion_point(class_scope:exchanger.UpdateRequest)
  })
_sym_db.RegisterMessage(UpdateRequest)

UpdateResponse = _reflection.GeneratedProtocolMessageType('UpdateResponse', (_message.Message,), {
  'DESCRIPTOR' : _UPDATERESPONSE,
  '__module__' : 'exchanger_pb2'
  # @@protoc_insertion_point(class_scope:exchanger.UpdateResponse)
  })
_sym_db.RegisterMessage(UpdateResponse)



_EXCHANGERSERVICE = _descriptor.ServiceDescriptor(
  name='ExchangerService',
  full_name='exchanger.ExchangerService',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=851,
  serialized_end=1100,
  methods=[
  _descriptor.MethodDescriptor(
    name='Healthz',
    full_name='exchanger.ExchangerService.Healthz',
    index=0,
    containing_service=None,
    input_type=_HEALTHZREQUEST,
    output_type=_HEALTHZRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='UpdateInputTransaction',
    full_name='exchanger.ExchangerService.UpdateInputTransaction',
    index=1,
    containing_service=None,
    input_type=_UPDATEREQUEST,
    output_type=_UPDATERESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='UpdateOutputTransaction',
    full_name='exchanger.ExchangerService.UpdateOutputTransaction',
    index=2,
    containing_service=None,
    input_type=_UPDATEREQUEST,
    output_type=_UPDATERESPONSE,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_EXCHANGERSERVICE)

DESCRIPTOR.services_by_name['ExchangerService'] = _EXCHANGERSERVICE

# @@protoc_insertion_point(module_scope)
