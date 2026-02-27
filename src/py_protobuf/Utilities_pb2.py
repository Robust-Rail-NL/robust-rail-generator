
'Generated protocol buffer code.'
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0fUtilities.proto\x12\tmypackage"*\n\x0cTimeInterval\x12\r\n\x05start\x18\x01 \x01(\x01\x12\x0b\n\x03end\x18\x02 \x01(\x01*;\n\rSolverBackend\x12\t\n\x05MIPCL\x10\x00\x12\t\n\x05CPLEX\x10\x01\x12\x0b\n\x07LPSOLVE\x10\x02\x12\x07\n\x03CBC\x10\x03b\x06proto3')
_SOLVERBACKEND = DESCRIPTOR.enum_types_by_name['SolverBackend']
SolverBackend = enum_type_wrapper.EnumTypeWrapper(_SOLVERBACKEND)
MIPCL = 0
CPLEX = 1
LPSOLVE = 2
CBC = 3
_TIMEINTERVAL = DESCRIPTOR.message_types_by_name['TimeInterval']
TimeInterval = _reflection.GeneratedProtocolMessageType('TimeInterval', (_message.Message,), {'DESCRIPTOR': _TIMEINTERVAL, '__module__': 'Utilities_pb2'})
_sym_db.RegisterMessage(TimeInterval)
if (_descriptor._USE_C_DESCRIPTORS == False):
    DESCRIPTOR._options = None
    _SOLVERBACKEND._serialized_start = 74
    _SOLVERBACKEND._serialized_end = 133
    _TIMEINTERVAL._serialized_start = 30
    _TIMEINTERVAL._serialized_end = 72
