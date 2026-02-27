
'Generated protocol buffer code.'
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1dHIP_protos/Location_HIP.proto\x12\rmypackage_hip"\x91\x01\n\x08Location\x12,\n\ntrackParts\x18\x01 \x03(\x0b2\x18.mypackage_hip.TrackPart\x12+\n\nfacilities\x18\x02 \x03(\x0b2\x17.mypackage_hip.Facility\x12*\n\ttaskTypes\x18\x03 \x03(\x0b2\x17.mypackage_hip.TaskType"Q\n\x08Resource\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x15\n\x0btrackPartId\x18\x03 \x01(\x04H\x00\x12\x14\n\nfacilityId\x18\x04 \x01(\x04H\x00B\n\n\x08resource"\x8b\x01\n\x08Facility\x12\n\n\x02id\x18\x01 \x01(\x04\x12\x0c\n\x04type\x18\x02 \x01(\t\x12\x19\n\x11relatedTrackParts\x18\x03 \x03(\x04\x12*\n\ttaskTypes\x18\x04 \x03(\x0b2\x17.mypackage_hip.TaskType\x12\x1e\n\x16simultaneousUsageCount\x18\x05 \x01(\r"\xb3\x01\n\tTrackPart\x12\n\n\x02id\x18\x01 \x01(\x04\x12*\n\x04type\x18\x02 \x01(\x0e2\x1c.mypackage_hip.TrackPartType\x12\r\n\x05aSide\x18\x03 \x03(\x04\x12\r\n\x05bSide\x18\x04 \x03(\x04\x12\x0e\n\x06length\x18\x05 \x01(\x01\x12\x0c\n\x04name\x18\x06 \x01(\t\x12\x1a\n\x12sawMovementAllowed\x18\x07 \x01(\x08\x12\x16\n\x0eparkingAllowed\x18\x08 \x01(\x08"`\n\x08TaskType\x127\n\npredefined\x18\x01 \x01(\x0e2!.mypackage_hip.PredefinedTaskTypeH\x00\x12\x0f\n\x05other\x18\x02 \x01(\tH\x00B\n\n\x08taskType*q\n\rTrackPartType\x12\x0c\n\x08RailRoad\x10\x00\x12\n\n\x06Switch\x10\x01\x12\x11\n\rEnglishSwitch\x10\x02\x12\x15\n\x11HalfEnglishSwitch\x10\x03\x12\x10\n\x0cIntersection\x10\x04\x12\n\n\x06Bumper\x10\x05*V\n\x12PredefinedTaskType\x12\x08\n\x04Move\x10\x00\x12\t\n\x05Split\x10\x01\x12\x0b\n\x07Combine\x10\x02\x12\x08\n\x04Wait\x10\x03\x12\n\n\x06Arrive\x10\x04\x12\x08\n\x04Exit\x10\x05b\x06proto3')
_TRACKPARTTYPE = DESCRIPTOR.enum_types_by_name['TrackPartType']
TrackPartType = enum_type_wrapper.EnumTypeWrapper(_TRACKPARTTYPE)
_PREDEFINEDTASKTYPE = DESCRIPTOR.enum_types_by_name['PredefinedTaskType']
PredefinedTaskType = enum_type_wrapper.EnumTypeWrapper(_PREDEFINEDTASKTYPE)
RailRoad = 0
Switch = 1
EnglishSwitch = 2
HalfEnglishSwitch = 3
Intersection = 4
Bumper = 5
Move = 0
Split = 1
Combine = 2
Wait = 3
Arrive = 4
Exit = 5
_LOCATION = DESCRIPTOR.message_types_by_name['Location']
_RESOURCE = DESCRIPTOR.message_types_by_name['Resource']
_FACILITY = DESCRIPTOR.message_types_by_name['Facility']
_TRACKPART = DESCRIPTOR.message_types_by_name['TrackPart']
_TASKTYPE = DESCRIPTOR.message_types_by_name['TaskType']
Location = _reflection.GeneratedProtocolMessageType('Location', (_message.Message,), {'DESCRIPTOR': _LOCATION, '__module__': 'HIP_protos.Location_HIP_pb2'})
_sym_db.RegisterMessage(Location)
Resource = _reflection.GeneratedProtocolMessageType('Resource', (_message.Message,), {'DESCRIPTOR': _RESOURCE, '__module__': 'HIP_protos.Location_HIP_pb2'})
_sym_db.RegisterMessage(Resource)
Facility = _reflection.GeneratedProtocolMessageType('Facility', (_message.Message,), {'DESCRIPTOR': _FACILITY, '__module__': 'HIP_protos.Location_HIP_pb2'})
_sym_db.RegisterMessage(Facility)
TrackPart = _reflection.GeneratedProtocolMessageType('TrackPart', (_message.Message,), {'DESCRIPTOR': _TRACKPART, '__module__': 'HIP_protos.Location_HIP_pb2'})
_sym_db.RegisterMessage(TrackPart)
TaskType = _reflection.GeneratedProtocolMessageType('TaskType', (_message.Message,), {'DESCRIPTOR': _TASKTYPE, '__module__': 'HIP_protos.Location_HIP_pb2'})
_sym_db.RegisterMessage(TaskType)
if (_descriptor._USE_C_DESCRIPTORS == False):
    DESCRIPTOR._options = None
    _TRACKPARTTYPE._serialized_start = 701
    _TRACKPARTTYPE._serialized_end = 814
    _PREDEFINEDTASKTYPE._serialized_start = 816
    _PREDEFINEDTASKTYPE._serialized_end = 902
    _LOCATION._serialized_start = 49
    _LOCATION._serialized_end = 194
    _RESOURCE._serialized_start = 196
    _RESOURCE._serialized_end = 277
    _FACILITY._serialized_start = 280
    _FACILITY._serialized_end = 419
    _TRACKPART._serialized_start = 422
    _TRACKPART._serialized_end = 601
    _TASKTYPE._serialized_start = 603
    _TASKTYPE._serialized_end = 699
