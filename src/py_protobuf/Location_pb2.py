
'Generated protocol buffer code.'
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from . import Utilities_pb2 as Utilities__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0eLocation.proto\x12\tmypackage\x1a\x0fUtilities.proto"\x9e\x02\n\x08Location\x12(\n\ntrackParts\x18\x01 \x03(\x0b2\x14.mypackage.TrackPart\x12\'\n\nfacilities\x18\x02 \x03(\x0b2\x13.mypackage.Facility\x12&\n\ttaskTypes\x18\x03 \x03(\x0b2\x13.mypackage.TaskType\x12\x18\n\x10movementConstant\x18\x04 \x01(\x11\x12 \n\x18movementTrackCoefficient\x18\x05 \x01(\x11\x12!\n\x19movementSwitchCoefficient\x18\x06 \x01(\x11\x128\n\x0fdistanceEntries\x18\x07 \x03(\x0b2\x1f.mypackage.WalkingDistanceEntry"d\n\x08Resource\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x15\n\x0btrackPartId\x18\x03 \x01(\x04H\x00\x12\x14\n\nfacilityId\x18\x04 \x01(\x04H\x00\x12\x11\n\x07staffId\x18\x05 \x01(\x04H\x00B\n\n\x08resource"\xb4\x01\n\x08Facility\x12\n\n\x02id\x18\x01 \x01(\x04\x12\x0c\n\x04type\x18\x02 \x01(\t\x12\x19\n\x11relatedTrackParts\x18\x03 \x03(\x04\x12&\n\ttaskTypes\x18\x04 \x03(\x0b2\x13.mypackage.TaskType\x12\x1e\n\x16simultaneousUsageCount\x18\x05 \x01(\r\x12+\n\ntimeWindow\x18\x06 \x01(\x0b2\x17.mypackage.TimeInterval"\xdf\x01\n\tTrackPart\x12\n\n\x02id\x18\x01 \x01(\x04\x12&\n\x04type\x18\x02 \x01(\x0e2\x18.mypackage.TrackPartType\x12\r\n\x05aSide\x18\x03 \x03(\x04\x12\r\n\x05bSide\x18\x04 \x03(\x04\x12\x0e\n\x06length\x18\x05 \x01(\x01\x12\x0c\n\x04name\x18\x06 \x01(\t\x12\x1a\n\x12sawMovementAllowed\x18\x07 \x01(\x08\x12\x16\n\x0eparkingAllowed\x18\x08 \x01(\x08\x12\x15\n\risElectrified\x18\t \x01(\x08\x12\x17\n\x0fstationPlatform\x18\n \x01(\x08"\\\n\x08TaskType\x123\n\npredefined\x18\x01 \x01(\x0e2\x1d.mypackage.PredefinedTaskTypeH\x00\x12\x0f\n\x05other\x18\x02 \x01(\tH\x00B\n\n\x08taskType"a\n\x14WalkingDistanceEntry\x12\x17\n\x0ffromTrackPartId\x18\x01 \x01(\x04\x12\x15\n\rtoTrackPartId\x18\x02 \x01(\x04\x12\x19\n\x11distanceInSeconds\x18\x03 \x01(\x01*\x83\x01\n\rTrackPartType\x12\x0c\n\x08RailRoad\x10\x00\x12\n\n\x06Switch\x10\x01\x12\x11\n\rEnglishSwitch\x10\x02\x12\x19\n\x11HalfEnglishSwitch\x10\x03\x1a\x02\x08\x01\x12\x10\n\x0cIntersection\x10\x04\x12\n\n\x06Bumper\x10\x05\x12\x0c\n\x08Building\x10\x06*\x9a\x01\n\x12PredefinedTaskType\x12\x08\n\x04Move\x10\x00\x12\t\n\x05Split\x10\x01\x12\x0b\n\x07Combine\x10\x02\x12\x08\n\x04Wait\x10\x03\x12\n\n\x06Arrive\x10\x04\x12\x08\n\x04Exit\x10\x05\x12\x0b\n\x07Walking\x10\x06\x12\t\n\x05Break\x10\x07\x12\x0e\n\nNonService\x10\x08\x12\r\n\tBeginMove\x10\t\x12\x0b\n\x07EndMove\x10\n*(\n\x04Side\x12\n\n\x06NoSide\x10\x00\x12\x05\n\x01A\x10\x01\x12\x05\n\x01B\x10\x02\x12\x06\n\x02AB\x10\x03b\x06proto3')
_TRACKPARTTYPE = DESCRIPTOR.enum_types_by_name['TrackPartType']
TrackPartType = enum_type_wrapper.EnumTypeWrapper(_TRACKPARTTYPE)
_PREDEFINEDTASKTYPE = DESCRIPTOR.enum_types_by_name['PredefinedTaskType']
PredefinedTaskType = enum_type_wrapper.EnumTypeWrapper(_PREDEFINEDTASKTYPE)
_SIDE = DESCRIPTOR.enum_types_by_name['Side']
Side = enum_type_wrapper.EnumTypeWrapper(_SIDE)
RailRoad = 0
Switch = 1
EnglishSwitch = 2
HalfEnglishSwitch = 3
Intersection = 4
Bumper = 5
Building = 6
Move = 0
Split = 1
Combine = 2
Wait = 3
Arrive = 4
Exit = 5
Walking = 6
Break = 7
NonService = 8
BeginMove = 9
EndMove = 10
NoSide = 0
A = 1
B = 2
AB = 3
_LOCATION = DESCRIPTOR.message_types_by_name['Location']
_RESOURCE = DESCRIPTOR.message_types_by_name['Resource']
_FACILITY = DESCRIPTOR.message_types_by_name['Facility']
_TRACKPART = DESCRIPTOR.message_types_by_name['TrackPart']
_TASKTYPE = DESCRIPTOR.message_types_by_name['TaskType']
_WALKINGDISTANCEENTRY = DESCRIPTOR.message_types_by_name['WalkingDistanceEntry']
Location = _reflection.GeneratedProtocolMessageType('Location', (_message.Message,), {'DESCRIPTOR': _LOCATION, '__module__': 'Location_pb2'})
_sym_db.RegisterMessage(Location)
Resource = _reflection.GeneratedProtocolMessageType('Resource', (_message.Message,), {'DESCRIPTOR': _RESOURCE, '__module__': 'Location_pb2'})
_sym_db.RegisterMessage(Resource)
Facility = _reflection.GeneratedProtocolMessageType('Facility', (_message.Message,), {'DESCRIPTOR': _FACILITY, '__module__': 'Location_pb2'})
_sym_db.RegisterMessage(Facility)
TrackPart = _reflection.GeneratedProtocolMessageType('TrackPart', (_message.Message,), {'DESCRIPTOR': _TRACKPART, '__module__': 'Location_pb2'})
_sym_db.RegisterMessage(TrackPart)
TaskType = _reflection.GeneratedProtocolMessageType('TaskType', (_message.Message,), {'DESCRIPTOR': _TASKTYPE, '__module__': 'Location_pb2'})
_sym_db.RegisterMessage(TaskType)
WalkingDistanceEntry = _reflection.GeneratedProtocolMessageType('WalkingDistanceEntry', (_message.Message,), {'DESCRIPTOR': _WALKINGDISTANCEENTRY, '__module__': 'Location_pb2'})
_sym_db.RegisterMessage(WalkingDistanceEntry)
if (_descriptor._USE_C_DESCRIPTORS == False):
    DESCRIPTOR._options = None
    _TRACKPARTTYPE.values_by_name['HalfEnglishSwitch']._options = None
    _TRACKPARTTYPE.values_by_name['HalfEnglishSwitch']._serialized_options = b'\x08\x01'
    _TRACKPARTTYPE._serialized_start = 1040
    _TRACKPARTTYPE._serialized_end = 1171
    _PREDEFINEDTASKTYPE._serialized_start = 1174
    _PREDEFINEDTASKTYPE._serialized_end = 1328
    _SIDE._serialized_start = 1330
    _SIDE._serialized_end = 1370
    _LOCATION._serialized_start = 47
    _LOCATION._serialized_end = 333
    _RESOURCE._serialized_start = 335
    _RESOURCE._serialized_end = 435
    _FACILITY._serialized_start = 438
    _FACILITY._serialized_end = 618
    _TRACKPART._serialized_start = 621
    _TRACKPART._serialized_end = 844
    _TASKTYPE._serialized_start = 846
    _TASKTYPE._serialized_end = 938
    _WALKINGDISTANCEENTRY._serialized_start = 940
    _WALKINGDISTANCEENTRY._serialized_end = 1037
