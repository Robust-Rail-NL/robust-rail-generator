
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from . import Location_pb2 as Location__pb2
from . import TrainUnitTypes_pb2 as TrainUnitTypes__pb2
from . import Utilities_pb2 as Utilities__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0eScenario.proto\x12\tmypackage\x1a\x0eLocation.proto\x1a\x14TrainUnitTypes.proto\x1a\x0fUtilities.proto"\x87\x03\n\x08Scenario\x12\x1c\n\x02in\x18\x06 \x03(\x0b2\x10.mypackage.Train\x12$\n\ninStanding\x18\n \x03(\x0b2\x10.mypackage.Train\x12\x1d\n\x03out\x18\x07 \x03(\x0b2\x10.mypackage.Train\x12%\n\x0boutStanding\x18\x0b \x03(\x0b2\x10.mypackage.Train\x127\n\x11nonServiceTraffic\x18\x03 \x03(\x0b2\x1c.mypackage.NonServiceTraffic\x127\n\x11disabledTrackPart\x18\x04 \x03(\x0b2\x1c.mypackage.DisabledTrackPart\x12)\n\x07workers\x18\x05 \x03(\x0b2\x18.mypackage.MemberOfStaff\x12\x11\n\tstartTime\x18\x08 \x01(\x04\x12\x0f\n\x07endTime\x18\t \x01(\x04\x120\n\x0etrainUnitTypes\x18\x0c \x03(\x0b2\x18.mypackage.TrainUnitType"\xc8\x01\n\x05Train\x12\x15\n\rsideTrackPart\x18\x06 \x01(\x04\x12\x18\n\x10parkingTrackPart\x18\x07 \x01(\x04\x12\x0c\n\x04time\x18\x02 \x01(\x04\x12\n\n\x02id\x18\x03 \x01(\t\x12%\n\x07members\x18\x08 \x03(\x0b2\x14.mypackage.TrainUnit\x12\x1d\n\x15canDepartFromAnyTrack\x18\t \x01(\x08\x12\x15\n\rstandingIndex\x18\n \x01(\x01\x12\x17\n\x0fminimumDuration\x18\x0b \x01(\t"T\n\x11NonServiceTraffic\x12\x0f\n\x07members\x18\x01 \x03(\x04\x12\x0f\n\x07arrival\x18\x02 \x01(\x04\x12\x11\n\tdeparture\x18\x03 \x01(\x04\x12\n\n\x02id\x18\x04 \x01(\t"J\n\x11DisabledTrackPart\x12\x11\n\ttrackPart\x18\x01 \x01(\x04\x12\x0f\n\x07arrival\x18\x02 \x01(\x04\x12\x11\n\tdeparture\x18\x03 \x01(\x04"T\n\tTrainUnit\x12\n\n\x02id\x18\x01 \x01(\t\x12\x17\n\x0ftypeDisplayName\x18\x02 \x01(\t\x12"\n\x05tasks\x18\x03 \x03(\x0b2\x13.mypackage.TaskSpec"P\n\x0cShuntingUnit\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0f\n\x07members\x18\x02 \x03(\t\x12\x11\n\tparentIDs\x18\x03 \x03(\t\x12\x10\n\x08childIDs\x18\x04 \x03(\t"i\n\x08TaskSpec\x12!\n\x04type\x18\x01 \x01(\x0b2\x13.mypackage.TaskType\x12\x10\n\x08priority\x18\x02 \x01(\r\x12\x10\n\x08duration\x18\x03 \x01(\x04\x12\x16\n\x0erequiredSkills\x18\x04 \x03(\t"\x96\x02\n\rMemberOfStaff\x12\n\n\x02id\x18\x01 \x01(\x04\x12\x0c\n\x04type\x18\x02 \x01(\t\x12\x0e\n\x06skills\x18\x03 \x03(\t\x12\'\n\x06shifts\x18\x04 \x03(\x0b2\x17.mypackage.TimeInterval\x12-\n\x0cbreakWindows\x18\x05 \x03(\x0b2\x17.mypackage.TimeInterval\x12\x15\n\rbreakDuration\x18\x06 \x01(\x01\x12\x17\n\x0fstartLocationId\x18\x07 \x01(\x04\x12\x15\n\rendLocationId\x18\x08 \x01(\x04\x12\x15\n\rcanMoveTrains\x18\t \x01(\x08\x12\x0c\n\x04name\x18\n \x01(\t\x12\x17\n\x0fbreakLocationId\x18\x0b \x01(\x04b\x06proto3')
_SCENARIO = DESCRIPTOR.message_types_by_name['Scenario']
_TRAIN = DESCRIPTOR.message_types_by_name['Train']
_NONSERVICETRAFFIC = DESCRIPTOR.message_types_by_name['NonServiceTraffic']
_DISABLEDTRACKPART = DESCRIPTOR.message_types_by_name['DisabledTrackPart']
_TRAINUNIT = DESCRIPTOR.message_types_by_name['TrainUnit']
_SHUNTINGUNIT = DESCRIPTOR.message_types_by_name['ShuntingUnit']
_TASKSPEC = DESCRIPTOR.message_types_by_name['TaskSpec']
_MEMBEROFSTAFF = DESCRIPTOR.message_types_by_name['MemberOfStaff']
Scenario = _reflection.GeneratedProtocolMessageType('Scenario', (_message.Message,), {'DESCRIPTOR': _SCENARIO, '__module__': 'Scenario_pb2'})
_sym_db.RegisterMessage(Scenario)
Train = _reflection.GeneratedProtocolMessageType('Train', (_message.Message,), {'DESCRIPTOR': _TRAIN, '__module__': 'Scenario_pb2'})
_sym_db.RegisterMessage(Train)
NonServiceTraffic = _reflection.GeneratedProtocolMessageType('NonServiceTraffic', (_message.Message,), {'DESCRIPTOR': _NONSERVICETRAFFIC, '__module__': 'Scenario_pb2'})
_sym_db.RegisterMessage(NonServiceTraffic)
DisabledTrackPart = _reflection.GeneratedProtocolMessageType('DisabledTrackPart', (_message.Message,), {'DESCRIPTOR': _DISABLEDTRACKPART, '__module__': 'Scenario_pb2'})
_sym_db.RegisterMessage(DisabledTrackPart)
TrainUnit = _reflection.GeneratedProtocolMessageType('TrainUnit', (_message.Message,), {'DESCRIPTOR': _TRAINUNIT, '__module__': 'Scenario_pb2'})
_sym_db.RegisterMessage(TrainUnit)
ShuntingUnit = _reflection.GeneratedProtocolMessageType('ShuntingUnit', (_message.Message,), {'DESCRIPTOR': _SHUNTINGUNIT, '__module__': 'Scenario_pb2'})
_sym_db.RegisterMessage(ShuntingUnit)
TaskSpec = _reflection.GeneratedProtocolMessageType('TaskSpec', (_message.Message,), {'DESCRIPTOR': _TASKSPEC, '__module__': 'Scenario_pb2'})
_sym_db.RegisterMessage(TaskSpec)
MemberOfStaff = _reflection.GeneratedProtocolMessageType('MemberOfStaff', (_message.Message,), {'DESCRIPTOR': _MEMBEROFSTAFF, '__module__': 'Scenario_pb2'})
_sym_db.RegisterMessage(MemberOfStaff)
if (_descriptor._USE_C_DESCRIPTORS == False):
    DESCRIPTOR._options = None
    _SCENARIO._serialized_start = 85
    _SCENARIO._serialized_end = 476
    _TRAIN._serialized_start = 479
    _TRAIN._serialized_end = 679
    _NONSERVICETRAFFIC._serialized_start = 681
    _NONSERVICETRAFFIC._serialized_end = 765
    _DISABLEDTRACKPART._serialized_start = 767
    _DISABLEDTRACKPART._serialized_end = 841
    _TRAINUNIT._serialized_start = 843
    _TRAINUNIT._serialized_end = 927
    _SHUNTINGUNIT._serialized_start = 929
    _SHUNTINGUNIT._serialized_end = 1009
    _TASKSPEC._serialized_start = 1011
    _TASKSPEC._serialized_end = 1116
    _MEMBEROFSTAFF._serialized_start = 1119
    _MEMBEROFSTAFF._serialized_end = 1397
