# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: dev_observer/api/types/schedule.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'dev_observer/api/types/schedule.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n%dev_observer/api/types/schedule.proto\x12\x1f\x64\x65v_observer.api.types.schedule\"I\n\x08Schedule\x12=\n\tfrequency\x18\x01 \x01(\x0b\x32*.dev_observer.api.types.schedule.Frequency\"\xd9\x02\n\tFrequency\x12\x41\n\x05\x64\x61ily\x18\x64 \x01(\x0b\x32\x30.dev_observer.api.types.schedule.Frequency.DailyH\x00\x12\x43\n\x06weekly\x18\x65 \x01(\x0b\x32\x31.dev_observer.api.types.schedule.Frequency.WeeklyH\x00\x1a<\n\x05\x44\x61ily\x12\x33\n\x04time\x18\x01 \x01(\x0b\x32%.dev_observer.api.types.schedule.Time\x1a~\n\x06Weekly\x12?\n\x0b\x64\x61y_of_week\x18\x01 \x01(\x0e\x32*.dev_observer.api.types.schedule.DayOfWeek\x12\x33\n\x04time\x18\x02 \x01(\x0b\x32%.dev_observer.api.types.schedule.TimeB\x06\n\x04type\"+\n\tTimeOfDay\x12\r\n\x05hours\x18\x01 \x01(\x05\x12\x0f\n\x07minutes\x18\x02 \x01(\x05\"\x85\x01\n\x04Time\x12?\n\x0btime_of_day\x18\x01 \x01(\x0b\x32*.dev_observer.api.types.schedule.TimeOfDay\x12<\n\ttime_zone\x18\x02 \x01(\x0b\x32).dev_observer.api.types.schedule.TimeZone\"\x16\n\x08TimeZone\x12\n\n\x02id\x18\x01 \x01(\t*\x84\x01\n\tDayOfWeek\x12\x1b\n\x17\x44\x41Y_OF_WEEK_UNSPECIFIED\x10\x00\x12\n\n\x06MONDAY\x10\x01\x12\x0b\n\x07TUESDAY\x10\x02\x12\r\n\tWEDNESDAY\x10\x03\x12\x0c\n\x08THURSDAY\x10\x04\x12\n\n\x06\x46RIDAY\x10\x05\x12\x0c\n\x08SATURDAY\x10\x06\x12\n\n\x06SUNDAY\x10\x07\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'dev_observer.api.types.schedule_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_DAYOFWEEK']._serialized_start=703
  _globals['_DAYOFWEEK']._serialized_end=835
  _globals['_SCHEDULE']._serialized_start=74
  _globals['_SCHEDULE']._serialized_end=147
  _globals['_FREQUENCY']._serialized_start=150
  _globals['_FREQUENCY']._serialized_end=495
  _globals['_FREQUENCY_DAILY']._serialized_start=299
  _globals['_FREQUENCY_DAILY']._serialized_end=359
  _globals['_FREQUENCY_WEEKLY']._serialized_start=361
  _globals['_FREQUENCY_WEEKLY']._serialized_end=487
  _globals['_TIMEOFDAY']._serialized_start=497
  _globals['_TIMEOFDAY']._serialized_end=540
  _globals['_TIME']._serialized_start=543
  _globals['_TIME']._serialized_end=676
  _globals['_TIMEZONE']._serialized_start=678
  _globals['_TIMEZONE']._serialized_end=700
# @@protoc_insertion_point(module_scope)
