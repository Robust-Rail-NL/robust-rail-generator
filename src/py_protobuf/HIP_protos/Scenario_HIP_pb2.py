
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from ..HIP_protos import Location_HIP_pb2 as HIP__protos_dot_Location__HIP__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1dHIP_protos/Scenario_HIP.proto\x12\rmypackage_hip\x1a\x1dHIP_protos/Location_HIP.proto"\xee\x01\n\x08Scenario\x12%\n\x02in\x18\x01 \x01(\x0b2\x19.mypackage_hip.ScenarioIn\x12\'\n\x03out\x18\x02 \x01(\x0b2\x1a.mypackage_hip.ScenarioOut\x125\n\ninStanding\x18\x03 \x01(\x0b2!.mypackage_hip.ScenarioInStanding\x127\n\x0boutStanding\x18\x04 \x01(\x0b2".mypackage_hip.ScenarioOutStanding\x12\x11\n\tstartTime\x18\x05 \x01(\x04\x12\x0f\n\x07endTime\x18\x06 \x01(\x04":\n\nScenarioIn\x12,\n\x06trains\x18\x01 \x03(\x0b2\x1c.mypackage_hip.IncomingTrain"A\n\x0bScenarioOut\x122\n\rtrainRequests\x18\x01 \x03(\x0b2\x1b.mypackage_hip.TrainRequest"B\n\x12ScenarioInStanding\x12,\n\x06trains\x18\x01 \x03(\x0b2\x1c.mypackage_hip.IncomingTrain"I\n\x13ScenarioOutStanding\x122\n\rtrainRequests\x18\x01 \x03(\x0b2\x1b.mypackage_hip.TrainRequest"\xa9\x01\n\rIncomingTrain\x12\x16\n\x0eentryTrackPart\x18\x01 \x01(\x04\x12\x1d\n\x15firstParkingTrackPart\x18\x06 \x01(\x04\x12\x0f\n\x07arrival\x18\x02 \x01(\x04\x12\x11\n\tdeparture\x18\x03 \x01(\x04\x12\n\n\x02id\x18\x04 \x01(\t\x121\n\x07members\x18\x05 \x03(\x0b2 .mypackage_hip.IncomingTrainUnit"h\n\x11IncomingTrainUnit\x12+\n\ttrainUnit\x18\x01 \x01(\x0b2\x18.mypackage_hip.TrainUnit\x12&\n\x05tasks\x18\x02 \x03(\x0b2\x17.mypackage_hip.TaskSpec"\xc2\x01\n\x0cTrainRequest\x12\x16\n\x0eleaveTrackPart\x18\x01 \x01(\x04\x12\x1c\n\x14lastParkingTrackPart\x18\x06 \x01(\x04\x12\x0f\n\x07arrival\x18\x02 \x01(\x04\x12\x11\n\tdeparture\x18\x03 \x01(\x04\x12\x13\n\x0bdisplayName\x18\x04 \x01(\t\x12,\n\ntrainUnits\x18\x05 \x03(\x0b2\x18.mypackage_hip.TrainUnit\x12\x15\n\rstandingIndex\x18\x07 \x01(\x01"C\n\tTrainUnit\x12\n\n\x02id\x18\x01 \x01(\t\x12*\n\x04type\x18\x02 \x01(\x0b2\x1c.mypackage_hip.TrainUnitType"\xc1\x01\n\rTrainUnitType\x12\x13\n\x0bdisplayName\x18\x01 \x01(\t\x12\x11\n\tcarriages\x18\x02 \x01(\r\x12\x0e\n\x06length\x18\x04 \x01(\x01\x12\x18\n\x10reversalDuration\x18\x03 \x01(\x04\x12\x17\n\x0fcombineDuration\x18\x05 \x01(\x04\x12\x15\n\rsplitDuration\x18\x06 \x01(\x04\x12\x14\n\x0cbackNormTime\x18\x07 \x01(\x04\x12\x18\n\x10backAdditionTime\x18\x08 \x01(\x04"\x80\x01\n\x0cShuntingUnit\x12\n\n\x02id\x18\x01 \x01(\t\x12)\n\x07members\x18\x02 \x03(\x0b2\x18.mypackage_hip.TrainUnit\x12\x11\n\tparentIDs\x18\x03 \x03(\t\x12\x10\n\x08childIDs\x18\x04 \x03(\t\x12\x14\n\x0cstandingType\x18\x05 \x01(\t"Y\n\x08TaskSpec\x12%\n\x04type\x18\x01 \x01(\x0b2\x17.mypackage_hip.TaskType\x12\x14\n\x08priority\x18\x02 \x01(\rB\x02\x18\x01\x12\x10\n\x08duration\x18\x03 \x01(\x04b\x06proto3')
_SCENARIO = DESCRIPTOR.message_types_by_name['Scenario']
_SCENARIOIN = DESCRIPTOR.message_types_by_name['ScenarioIn']
_SCENARIOOUT = DESCRIPTOR.message_types_by_name['ScenarioOut']
_SCENARIOINSTANDING = DESCRIPTOR.message_types_by_name['ScenarioInStanding']
_SCENARIOOUTSTANDING = DESCRIPTOR.message_types_by_name['ScenarioOutStanding']
_INCOMINGTRAIN = DESCRIPTOR.message_types_by_name['IncomingTrain']
_INCOMINGTRAINUNIT = DESCRIPTOR.message_types_by_name['IncomingTrainUnit']
_TRAINREQUEST = DESCRIPTOR.message_types_by_name['TrainRequest']
_TRAINUNIT = DESCRIPTOR.message_types_by_name['TrainUnit']
_TRAINUNITTYPE = DESCRIPTOR.message_types_by_name['TrainUnitType']
_SHUNTINGUNIT = DESCRIPTOR.message_types_by_name['ShuntingUnit']
_TASKSPEC = DESCRIPTOR.message_types_by_name['TaskSpec']
Scenario = _reflection.GeneratedProtocolMessageType('Scenario', (_message.Message,), {'DESCRIPTOR': _SCENARIO, '__module__': 'HIP_protos.Scenario_HIP_pb2'})
_sym_db.RegisterMessage(Scenario)
ScenarioIn = _reflection.GeneratedProtocolMessageType('ScenarioIn', (_message.Message,), {'DESCRIPTOR': _SCENARIOIN, '__module__': 'HIP_protos.Scenario_HIP_pb2'})
_sym_db.RegisterMessage(ScenarioIn)
ScenarioOut = _reflection.GeneratedProtocolMessageType('ScenarioOut', (_message.Message,), {'DESCRIPTOR': _SCENARIOOUT, '__module__': 'HIP_protos.Scenario_HIP_pb2'})
_sym_db.RegisterMessage(ScenarioOut)
ScenarioInStanding = _reflection.GeneratedProtocolMessageType('ScenarioInStanding', (_message.Message,), {'DESCRIPTOR': _SCENARIOINSTANDING, '__module__': 'HIP_protos.Scenario_HIP_pb2'})
_sym_db.RegisterMessage(ScenarioInStanding)
ScenarioOutStanding = _reflection.GeneratedProtocolMessageType('ScenarioOutStanding', (_message.Message,), {'DESCRIPTOR': _SCENARIOOUTSTANDING, '__module__': 'HIP_protos.Scenario_HIP_pb2'})
_sym_db.RegisterMessage(ScenarioOutStanding)
IncomingTrain = _reflection.GeneratedProtocolMessageType('IncomingTrain', (_message.Message,), {'DESCRIPTOR': _INCOMINGTRAIN, '__module__': 'HIP_protos.Scenario_HIP_pb2'})
_sym_db.RegisterMessage(IncomingTrain)
IncomingTrainUnit = _reflection.GeneratedProtocolMessageType('IncomingTrainUnit', (_message.Message,), {'DESCRIPTOR': _INCOMINGTRAINUNIT, '__module__': 'HIP_protos.Scenario_HIP_pb2'})
_sym_db.RegisterMessage(IncomingTrainUnit)
TrainRequest = _reflection.GeneratedProtocolMessageType('TrainRequest', (_message.Message,), {'DESCRIPTOR': _TRAINREQUEST, '__module__': 'HIP_protos.Scenario_HIP_pb2'})
_sym_db.RegisterMessage(TrainRequest)
TrainUnit = _reflection.GeneratedProtocolMessageType('TrainUnit', (_message.Message,), {'DESCRIPTOR': _TRAINUNIT, '__module__': 'HIP_protos.Scenario_HIP_pb2'})
_sym_db.RegisterMessage(TrainUnit)
TrainUnitType = _reflection.GeneratedProtocolMessageType('TrainUnitType', (_message.Message,), {'DESCRIPTOR': _TRAINUNITTYPE, '__module__': 'HIP_protos.Scenario_HIP_pb2'})
_sym_db.RegisterMessage(TrainUnitType)
ShuntingUnit = _reflection.GeneratedProtocolMessageType('ShuntingUnit', (_message.Message,), {'DESCRIPTOR': _SHUNTINGUNIT, '__module__': 'HIP_protos.Scenario_HIP_pb2'})
_sym_db.RegisterMessage(ShuntingUnit)
TaskSpec = _reflection.GeneratedProtocolMessageType('TaskSpec', (_message.Message,), {'DESCRIPTOR': _TASKSPEC, '__module__': 'HIP_protos.Scenario_HIP_pb2'})
_sym_db.RegisterMessage(TaskSpec)
if (_descriptor._USE_C_DESCRIPTORS == False):
    DESCRIPTOR._options = None
    _TASKSPEC.fields_by_name['priority']._options = None
    _TASKSPEC.fields_by_name['priority']._serialized_options = b'\x18\x01'
    _SCENARIO._serialized_start = 80
    _SCENARIO._serialized_end = 318
    _SCENARIOIN._serialized_start = 320
    _SCENARIOIN._serialized_end = 378
    _SCENARIOOUT._serialized_start = 380
    _SCENARIOOUT._serialized_end = 445
    _SCENARIOINSTANDING._serialized_start = 447
    _SCENARIOINSTANDING._serialized_end = 513
    _SCENARIOOUTSTANDING._serialized_start = 515
    _SCENARIOOUTSTANDING._serialized_end = 588
    _INCOMINGTRAIN._serialized_start = 591
    _INCOMINGTRAIN._serialized_end = 760
    _INCOMINGTRAINUNIT._serialized_start = 762
    _INCOMINGTRAINUNIT._serialized_end = 866
    _TRAINREQUEST._serialized_start = 869
    _TRAINREQUEST._serialized_end = 1063
    _TRAINUNIT._serialized_start = 1065
    _TRAINUNIT._serialized_end = 1132
    _TRAINUNITTYPE._serialized_start = 1135
    _TRAINUNITTYPE._serialized_end = 1328
    _SHUNTINGUNIT._serialized_start = 1331
    _SHUNTINGUNIT._serialized_end = 1459
    _TASKSPEC._serialized_start = 1461
    _TASKSPEC._serialized_end = 1550
