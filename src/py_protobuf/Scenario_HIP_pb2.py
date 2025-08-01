# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: Scenario_HIP.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import Location_HIP_pb2 as Location__HIP__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='Scenario_HIP.proto',
  package='mypackage_hip',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x12Scenario_HIP.proto\x12\rmypackage_hip\x1a\x12Location_HIP.proto\"\xee\x01\n\x08Scenario\x12%\n\x02in\x18\x01 \x01(\x0b\x32\x19.mypackage_hip.ScenarioIn\x12\'\n\x03out\x18\x02 \x01(\x0b\x32\x1a.mypackage_hip.ScenarioOut\x12\x35\n\ninStanding\x18\x03 \x01(\x0b\x32!.mypackage_hip.ScenarioInStanding\x12\x37\n\x0boutStanding\x18\x04 \x01(\x0b\x32\".mypackage_hip.ScenarioOutStanding\x12\x11\n\tstartTime\x18\x05 \x01(\x04\x12\x0f\n\x07\x65ndTime\x18\x06 \x01(\x04\":\n\nScenarioIn\x12,\n\x06trains\x18\x01 \x03(\x0b\x32\x1c.mypackage_hip.IncomingTrain\"A\n\x0bScenarioOut\x12\x32\n\rtrainRequests\x18\x01 \x03(\x0b\x32\x1b.mypackage_hip.TrainRequest\"B\n\x12ScenarioInStanding\x12,\n\x06trains\x18\x01 \x03(\x0b\x32\x1c.mypackage_hip.IncomingTrain\"I\n\x13ScenarioOutStanding\x12\x32\n\rtrainRequests\x18\x01 \x03(\x0b\x32\x1b.mypackage_hip.TrainRequest\"\xa9\x01\n\rIncomingTrain\x12\x16\n\x0e\x65ntryTrackPart\x18\x01 \x01(\x04\x12\x1d\n\x15\x66irstParkingTrackPart\x18\x06 \x01(\x04\x12\x0f\n\x07\x61rrival\x18\x02 \x01(\x04\x12\x11\n\tdeparture\x18\x03 \x01(\x04\x12\n\n\x02id\x18\x04 \x01(\t\x12\x31\n\x07members\x18\x05 \x03(\x0b\x32 .mypackage_hip.IncomingTrainUnit\"h\n\x11IncomingTrainUnit\x12+\n\ttrainUnit\x18\x01 \x01(\x0b\x32\x18.mypackage_hip.TrainUnit\x12&\n\x05tasks\x18\x02 \x03(\x0b\x32\x17.mypackage_hip.TaskSpec\"\xc2\x01\n\x0cTrainRequest\x12\x16\n\x0eleaveTrackPart\x18\x01 \x01(\x04\x12\x1c\n\x14lastParkingTrackPart\x18\x06 \x01(\x04\x12\x0f\n\x07\x61rrival\x18\x02 \x01(\x04\x12\x11\n\tdeparture\x18\x03 \x01(\x04\x12\x13\n\x0b\x64isplayName\x18\x04 \x01(\t\x12,\n\ntrainUnits\x18\x05 \x03(\x0b\x32\x18.mypackage_hip.TrainUnit\x12\x15\n\rstandingIndex\x18\x07 \x01(\x01\"C\n\tTrainUnit\x12\n\n\x02id\x18\x01 \x01(\t\x12*\n\x04type\x18\x02 \x01(\x0b\x32\x1c.mypackage_hip.TrainUnitType\"\xc1\x01\n\rTrainUnitType\x12\x13\n\x0b\x64isplayName\x18\x01 \x01(\t\x12\x11\n\tcarriages\x18\x02 \x01(\r\x12\x0e\n\x06length\x18\x04 \x01(\x01\x12\x18\n\x10reversalDuration\x18\x03 \x01(\x04\x12\x17\n\x0f\x63ombineDuration\x18\x05 \x01(\x04\x12\x15\n\rsplitDuration\x18\x06 \x01(\x04\x12\x14\n\x0c\x62\x61\x63kNormTime\x18\x07 \x01(\x04\x12\x18\n\x10\x62\x61\x63kAdditionTime\x18\x08 \x01(\x04\"j\n\x0cShuntingUnit\x12\n\n\x02id\x18\x01 \x01(\t\x12)\n\x07members\x18\x02 \x03(\x0b\x32\x18.mypackage_hip.TrainUnit\x12\x11\n\tparentIDs\x18\x03 \x03(\t\x12\x10\n\x08\x63hildIDs\x18\x04 \x03(\t\"Y\n\x08TaskSpec\x12%\n\x04type\x18\x01 \x01(\x0b\x32\x17.mypackage_hip.TaskType\x12\x14\n\x08priority\x18\x02 \x01(\rB\x02\x18\x01\x12\x10\n\x08\x64uration\x18\x03 \x01(\x04\x62\x06proto3'
  ,
  dependencies=[Location__HIP__pb2.DESCRIPTOR,])




_SCENARIO = _descriptor.Descriptor(
  name='Scenario',
  full_name='mypackage_hip.Scenario',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='in', full_name='mypackage_hip.Scenario.in', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='out', full_name='mypackage_hip.Scenario.out', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='inStanding', full_name='mypackage_hip.Scenario.inStanding', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='outStanding', full_name='mypackage_hip.Scenario.outStanding', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='startTime', full_name='mypackage_hip.Scenario.startTime', index=4,
      number=5, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='endTime', full_name='mypackage_hip.Scenario.endTime', index=5,
      number=6, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
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
  serialized_start=58,
  serialized_end=296,
)


_SCENARIOIN = _descriptor.Descriptor(
  name='ScenarioIn',
  full_name='mypackage_hip.ScenarioIn',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='trains', full_name='mypackage_hip.ScenarioIn.trains', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
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
  serialized_start=298,
  serialized_end=356,
)


_SCENARIOOUT = _descriptor.Descriptor(
  name='ScenarioOut',
  full_name='mypackage_hip.ScenarioOut',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='trainRequests', full_name='mypackage_hip.ScenarioOut.trainRequests', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
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
  serialized_start=358,
  serialized_end=423,
)


_SCENARIOINSTANDING = _descriptor.Descriptor(
  name='ScenarioInStanding',
  full_name='mypackage_hip.ScenarioInStanding',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='trains', full_name='mypackage_hip.ScenarioInStanding.trains', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
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
  serialized_start=425,
  serialized_end=491,
)


_SCENARIOOUTSTANDING = _descriptor.Descriptor(
  name='ScenarioOutStanding',
  full_name='mypackage_hip.ScenarioOutStanding',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='trainRequests', full_name='mypackage_hip.ScenarioOutStanding.trainRequests', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
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
  serialized_start=493,
  serialized_end=566,
)


_INCOMINGTRAIN = _descriptor.Descriptor(
  name='IncomingTrain',
  full_name='mypackage_hip.IncomingTrain',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='entryTrackPart', full_name='mypackage_hip.IncomingTrain.entryTrackPart', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='firstParkingTrackPart', full_name='mypackage_hip.IncomingTrain.firstParkingTrackPart', index=1,
      number=6, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='arrival', full_name='mypackage_hip.IncomingTrain.arrival', index=2,
      number=2, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='departure', full_name='mypackage_hip.IncomingTrain.departure', index=3,
      number=3, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='id', full_name='mypackage_hip.IncomingTrain.id', index=4,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='members', full_name='mypackage_hip.IncomingTrain.members', index=5,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
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
  serialized_start=569,
  serialized_end=738,
)


_INCOMINGTRAINUNIT = _descriptor.Descriptor(
  name='IncomingTrainUnit',
  full_name='mypackage_hip.IncomingTrainUnit',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='trainUnit', full_name='mypackage_hip.IncomingTrainUnit.trainUnit', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='tasks', full_name='mypackage_hip.IncomingTrainUnit.tasks', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
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
  serialized_start=740,
  serialized_end=844,
)


_TRAINREQUEST = _descriptor.Descriptor(
  name='TrainRequest',
  full_name='mypackage_hip.TrainRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='leaveTrackPart', full_name='mypackage_hip.TrainRequest.leaveTrackPart', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='lastParkingTrackPart', full_name='mypackage_hip.TrainRequest.lastParkingTrackPart', index=1,
      number=6, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='arrival', full_name='mypackage_hip.TrainRequest.arrival', index=2,
      number=2, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='departure', full_name='mypackage_hip.TrainRequest.departure', index=3,
      number=3, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='displayName', full_name='mypackage_hip.TrainRequest.displayName', index=4,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='trainUnits', full_name='mypackage_hip.TrainRequest.trainUnits', index=5,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='standingIndex', full_name='mypackage_hip.TrainRequest.standingIndex', index=6,
      number=7, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
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
  serialized_start=847,
  serialized_end=1041,
)


_TRAINUNIT = _descriptor.Descriptor(
  name='TrainUnit',
  full_name='mypackage_hip.TrainUnit',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='mypackage_hip.TrainUnit.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='type', full_name='mypackage_hip.TrainUnit.type', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
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
  serialized_start=1043,
  serialized_end=1110,
)


_TRAINUNITTYPE = _descriptor.Descriptor(
  name='TrainUnitType',
  full_name='mypackage_hip.TrainUnitType',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='displayName', full_name='mypackage_hip.TrainUnitType.displayName', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='carriages', full_name='mypackage_hip.TrainUnitType.carriages', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='length', full_name='mypackage_hip.TrainUnitType.length', index=2,
      number=4, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='reversalDuration', full_name='mypackage_hip.TrainUnitType.reversalDuration', index=3,
      number=3, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='combineDuration', full_name='mypackage_hip.TrainUnitType.combineDuration', index=4,
      number=5, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='splitDuration', full_name='mypackage_hip.TrainUnitType.splitDuration', index=5,
      number=6, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='backNormTime', full_name='mypackage_hip.TrainUnitType.backNormTime', index=6,
      number=7, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='backAdditionTime', full_name='mypackage_hip.TrainUnitType.backAdditionTime', index=7,
      number=8, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
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
  serialized_start=1113,
  serialized_end=1306,
)


_SHUNTINGUNIT = _descriptor.Descriptor(
  name='ShuntingUnit',
  full_name='mypackage_hip.ShuntingUnit',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='mypackage_hip.ShuntingUnit.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='members', full_name='mypackage_hip.ShuntingUnit.members', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='parentIDs', full_name='mypackage_hip.ShuntingUnit.parentIDs', index=2,
      number=3, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='childIDs', full_name='mypackage_hip.ShuntingUnit.childIDs', index=3,
      number=4, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
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
  serialized_start=1308,
  serialized_end=1414,
)


_TASKSPEC = _descriptor.Descriptor(
  name='TaskSpec',
  full_name='mypackage_hip.TaskSpec',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='mypackage_hip.TaskSpec.type', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='priority', full_name='mypackage_hip.TaskSpec.priority', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\030\001', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='duration', full_name='mypackage_hip.TaskSpec.duration', index=2,
      number=3, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
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
  serialized_start=1416,
  serialized_end=1505,
)

_SCENARIO.fields_by_name['in'].message_type = _SCENARIOIN
_SCENARIO.fields_by_name['out'].message_type = _SCENARIOOUT
_SCENARIO.fields_by_name['inStanding'].message_type = _SCENARIOINSTANDING
_SCENARIO.fields_by_name['outStanding'].message_type = _SCENARIOOUTSTANDING
_SCENARIOIN.fields_by_name['trains'].message_type = _INCOMINGTRAIN
_SCENARIOOUT.fields_by_name['trainRequests'].message_type = _TRAINREQUEST
_SCENARIOINSTANDING.fields_by_name['trains'].message_type = _INCOMINGTRAIN
_SCENARIOOUTSTANDING.fields_by_name['trainRequests'].message_type = _TRAINREQUEST
_INCOMINGTRAIN.fields_by_name['members'].message_type = _INCOMINGTRAINUNIT
_INCOMINGTRAINUNIT.fields_by_name['trainUnit'].message_type = _TRAINUNIT
_INCOMINGTRAINUNIT.fields_by_name['tasks'].message_type = _TASKSPEC
_TRAINREQUEST.fields_by_name['trainUnits'].message_type = _TRAINUNIT
_TRAINUNIT.fields_by_name['type'].message_type = _TRAINUNITTYPE
_SHUNTINGUNIT.fields_by_name['members'].message_type = _TRAINUNIT
_TASKSPEC.fields_by_name['type'].message_type = Location__HIP__pb2._TASKTYPE
DESCRIPTOR.message_types_by_name['Scenario'] = _SCENARIO
DESCRIPTOR.message_types_by_name['ScenarioIn'] = _SCENARIOIN
DESCRIPTOR.message_types_by_name['ScenarioOut'] = _SCENARIOOUT
DESCRIPTOR.message_types_by_name['ScenarioInStanding'] = _SCENARIOINSTANDING
DESCRIPTOR.message_types_by_name['ScenarioOutStanding'] = _SCENARIOOUTSTANDING
DESCRIPTOR.message_types_by_name['IncomingTrain'] = _INCOMINGTRAIN
DESCRIPTOR.message_types_by_name['IncomingTrainUnit'] = _INCOMINGTRAINUNIT
DESCRIPTOR.message_types_by_name['TrainRequest'] = _TRAINREQUEST
DESCRIPTOR.message_types_by_name['TrainUnit'] = _TRAINUNIT
DESCRIPTOR.message_types_by_name['TrainUnitType'] = _TRAINUNITTYPE
DESCRIPTOR.message_types_by_name['ShuntingUnit'] = _SHUNTINGUNIT
DESCRIPTOR.message_types_by_name['TaskSpec'] = _TASKSPEC
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Scenario = _reflection.GeneratedProtocolMessageType('Scenario', (_message.Message,), {
  'DESCRIPTOR' : _SCENARIO,
  '__module__' : 'Scenario_HIP_pb2'
  # @@protoc_insertion_point(class_scope:mypackage_hip.Scenario)
  })
_sym_db.RegisterMessage(Scenario)

ScenarioIn = _reflection.GeneratedProtocolMessageType('ScenarioIn', (_message.Message,), {
  'DESCRIPTOR' : _SCENARIOIN,
  '__module__' : 'Scenario_HIP_pb2'
  # @@protoc_insertion_point(class_scope:mypackage_hip.ScenarioIn)
  })
_sym_db.RegisterMessage(ScenarioIn)

ScenarioOut = _reflection.GeneratedProtocolMessageType('ScenarioOut', (_message.Message,), {
  'DESCRIPTOR' : _SCENARIOOUT,
  '__module__' : 'Scenario_HIP_pb2'
  # @@protoc_insertion_point(class_scope:mypackage_hip.ScenarioOut)
  })
_sym_db.RegisterMessage(ScenarioOut)

ScenarioInStanding = _reflection.GeneratedProtocolMessageType('ScenarioInStanding', (_message.Message,), {
  'DESCRIPTOR' : _SCENARIOINSTANDING,
  '__module__' : 'Scenario_HIP_pb2'
  # @@protoc_insertion_point(class_scope:mypackage_hip.ScenarioInStanding)
  })
_sym_db.RegisterMessage(ScenarioInStanding)

ScenarioOutStanding = _reflection.GeneratedProtocolMessageType('ScenarioOutStanding', (_message.Message,), {
  'DESCRIPTOR' : _SCENARIOOUTSTANDING,
  '__module__' : 'Scenario_HIP_pb2'
  # @@protoc_insertion_point(class_scope:mypackage_hip.ScenarioOutStanding)
  })
_sym_db.RegisterMessage(ScenarioOutStanding)

IncomingTrain = _reflection.GeneratedProtocolMessageType('IncomingTrain', (_message.Message,), {
  'DESCRIPTOR' : _INCOMINGTRAIN,
  '__module__' : 'Scenario_HIP_pb2'
  # @@protoc_insertion_point(class_scope:mypackage_hip.IncomingTrain)
  })
_sym_db.RegisterMessage(IncomingTrain)

IncomingTrainUnit = _reflection.GeneratedProtocolMessageType('IncomingTrainUnit', (_message.Message,), {
  'DESCRIPTOR' : _INCOMINGTRAINUNIT,
  '__module__' : 'Scenario_HIP_pb2'
  # @@protoc_insertion_point(class_scope:mypackage_hip.IncomingTrainUnit)
  })
_sym_db.RegisterMessage(IncomingTrainUnit)

TrainRequest = _reflection.GeneratedProtocolMessageType('TrainRequest', (_message.Message,), {
  'DESCRIPTOR' : _TRAINREQUEST,
  '__module__' : 'Scenario_HIP_pb2'
  # @@protoc_insertion_point(class_scope:mypackage_hip.TrainRequest)
  })
_sym_db.RegisterMessage(TrainRequest)

TrainUnit = _reflection.GeneratedProtocolMessageType('TrainUnit', (_message.Message,), {
  'DESCRIPTOR' : _TRAINUNIT,
  '__module__' : 'Scenario_HIP_pb2'
  # @@protoc_insertion_point(class_scope:mypackage_hip.TrainUnit)
  })
_sym_db.RegisterMessage(TrainUnit)

TrainUnitType = _reflection.GeneratedProtocolMessageType('TrainUnitType', (_message.Message,), {
  'DESCRIPTOR' : _TRAINUNITTYPE,
  '__module__' : 'Scenario_HIP_pb2'
  # @@protoc_insertion_point(class_scope:mypackage_hip.TrainUnitType)
  })
_sym_db.RegisterMessage(TrainUnitType)

ShuntingUnit = _reflection.GeneratedProtocolMessageType('ShuntingUnit', (_message.Message,), {
  'DESCRIPTOR' : _SHUNTINGUNIT,
  '__module__' : 'Scenario_HIP_pb2'
  # @@protoc_insertion_point(class_scope:mypackage_hip.ShuntingUnit)
  })
_sym_db.RegisterMessage(ShuntingUnit)

TaskSpec = _reflection.GeneratedProtocolMessageType('TaskSpec', (_message.Message,), {
  'DESCRIPTOR' : _TASKSPEC,
  '__module__' : 'Scenario_HIP_pb2'
  # @@protoc_insertion_point(class_scope:mypackage_hip.TaskSpec)
  })
_sym_db.RegisterMessage(TaskSpec)


_TASKSPEC.fields_by_name['priority']._options = None
# @@protoc_insertion_point(module_scope)
