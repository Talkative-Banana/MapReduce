# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: message.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rmessage.proto\x12\x07message\"\x1b\n\tFloatList\x12\x0e\n\x06values\x18\x01 \x03(\x02\"2\n\rFloatListList\x12!\n\x05lists\x18\x01 \x03(\x0b\x32\x12.message.FloatList\"Y\n\rRequestMapper\x12\x0f\n\x07indexes\x18\x01 \x03(\x05\x12%\n\x05\x63ords\x18\x02 \x01(\x0b\x32\x16.message.FloatListList\x12\x10\n\x08reducers\x18\x03 \x01(\x05\"\"\n\x0eResponseMapper\x12\x10\n\x08response\x18\x01 \x01(\x05\"!\n\x0eRequestReducer\x12\x0f\n\x07mappers\x18\x01 \x01(\x05\"L\n\x0fResponseReducer\x12\x10\n\x08response\x18\x01 \x01(\x05\x12\'\n\x07\x65ntries\x18\x02 \x01(\x0b\x32\x16.message.FloatListList2\x90\x01\n\x07Message\x12@\n\x0bServeMapper\x12\x16.message.RequestMapper\x1a\x17.message.ResponseMapper\"\x00\x12\x43\n\x0cServeReducer\x12\x17.message.RequestReducer\x1a\x18.message.ResponseReducer\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'message_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_FLOATLIST']._serialized_start=26
  _globals['_FLOATLIST']._serialized_end=53
  _globals['_FLOATLISTLIST']._serialized_start=55
  _globals['_FLOATLISTLIST']._serialized_end=105
  _globals['_REQUESTMAPPER']._serialized_start=107
  _globals['_REQUESTMAPPER']._serialized_end=196
  _globals['_RESPONSEMAPPER']._serialized_start=198
  _globals['_RESPONSEMAPPER']._serialized_end=232
  _globals['_REQUESTREDUCER']._serialized_start=234
  _globals['_REQUESTREDUCER']._serialized_end=267
  _globals['_RESPONSEREDUCER']._serialized_start=269
  _globals['_RESPONSEREDUCER']._serialized_end=345
  _globals['_MESSAGE']._serialized_start=348
  _globals['_MESSAGE']._serialized_end=492
# @@protoc_insertion_point(module_scope)
