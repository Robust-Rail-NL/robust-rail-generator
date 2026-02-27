
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14TrainUnitTypes.proto\x12\tmypackage"\xb4\x02\n\rTrainUnitType\x12\x13\n\x0bdisplayName\x18\x01 \x01(\t\x12\x11\n\tcarriages\x18\x02 \x01(\r\x12\x0e\n\x06length\x18\x04 \x01(\x01\x12\x17\n\x0fcombineDuration\x18\x05 \x01(\x04\x12\x15\n\rsplitDuration\x18\x06 \x01(\x04\x12\x14\n\x0cbackNormTime\x18\x07 \x01(\x04\x12\x18\n\x10backAdditionTime\x18\x08 \x01(\x04\x12\x13\n\x0btravelSpeed\x18\t \x01(\x04\x12\x13\n\x0bstartUpTime\x18\n \x01(\x04\x12\x12\n\ntypePrefix\x18\x0b \x01(\t\x12\x11\n\tneedsLoco\x18\x0c \x01(\x08\x12\x0e\n\x06isLoco\x18\r \x01(\x08\x12\x18\n\x10needsElectricity\x18\x0e \x01(\x08\x12\x10\n\x08idPrefix\x18\x0f \x01(\x05"9\n\x0eTrainUnitTypes\x12\'\n\x05types\x18\x01 \x03(\x0b2\x18.mypackage.TrainUnitTypeb\x06proto3')
_TRAINUNITTYPE = DESCRIPTOR.message_types_by_name['TrainUnitType']
_TRAINUNITTYPES = DESCRIPTOR.message_types_by_name['TrainUnitTypes']
TrainUnitType = _reflection.GeneratedProtocolMessageType('TrainUnitType', (_message.Message,), {'DESCRIPTOR': _TRAINUNITTYPE, '__module__': 'TrainUnitTypes_pb2'})
_sym_db.RegisterMessage(TrainUnitType)
TrainUnitTypes = _reflection.GeneratedProtocolMessageType('TrainUnitTypes', (_message.Message,), {'DESCRIPTOR': _TRAINUNITTYPES, '__module__': 'TrainUnitTypes_pb2'})
_sym_db.RegisterMessage(TrainUnitTypes)
if (_descriptor._USE_C_DESCRIPTORS == False):
    DESCRIPTOR._options = None
    _TRAINUNITTYPE._serialized_start = 36
    _TRAINUNITTYPE._serialized_end = 344
    _TRAINUNITTYPES._serialized_start = 346
    _TRAINUNITTYPES._serialized_end = 403
