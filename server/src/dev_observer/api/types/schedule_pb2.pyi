from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DayOfWeek(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DAY_OF_WEEK_UNSPECIFIED: _ClassVar[DayOfWeek]
    MONDAY: _ClassVar[DayOfWeek]
    TUESDAY: _ClassVar[DayOfWeek]
    WEDNESDAY: _ClassVar[DayOfWeek]
    THURSDAY: _ClassVar[DayOfWeek]
    FRIDAY: _ClassVar[DayOfWeek]
    SATURDAY: _ClassVar[DayOfWeek]
    SUNDAY: _ClassVar[DayOfWeek]
DAY_OF_WEEK_UNSPECIFIED: DayOfWeek
MONDAY: DayOfWeek
TUESDAY: DayOfWeek
WEDNESDAY: DayOfWeek
THURSDAY: DayOfWeek
FRIDAY: DayOfWeek
SATURDAY: DayOfWeek
SUNDAY: DayOfWeek

class Schedule(_message.Message):
    __slots__ = ("frequency",)
    FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    frequency: Frequency
    def __init__(self, frequency: _Optional[_Union[Frequency, _Mapping]] = ...) -> None: ...

class Frequency(_message.Message):
    __slots__ = ("daily", "weekly")
    class Daily(_message.Message):
        __slots__ = ("time",)
        TIME_FIELD_NUMBER: _ClassVar[int]
        time: Time
        def __init__(self, time: _Optional[_Union[Time, _Mapping]] = ...) -> None: ...
    class Weekly(_message.Message):
        __slots__ = ("day_of_week", "time")
        DAY_OF_WEEK_FIELD_NUMBER: _ClassVar[int]
        TIME_FIELD_NUMBER: _ClassVar[int]
        day_of_week: DayOfWeek
        time: Time
        def __init__(self, day_of_week: _Optional[_Union[DayOfWeek, str]] = ..., time: _Optional[_Union[Time, _Mapping]] = ...) -> None: ...
    DAILY_FIELD_NUMBER: _ClassVar[int]
    WEEKLY_FIELD_NUMBER: _ClassVar[int]
    daily: Frequency.Daily
    weekly: Frequency.Weekly
    def __init__(self, daily: _Optional[_Union[Frequency.Daily, _Mapping]] = ..., weekly: _Optional[_Union[Frequency.Weekly, _Mapping]] = ...) -> None: ...

class TimeOfDay(_message.Message):
    __slots__ = ("hours", "minutes")
    HOURS_FIELD_NUMBER: _ClassVar[int]
    MINUTES_FIELD_NUMBER: _ClassVar[int]
    hours: int
    minutes: int
    def __init__(self, hours: _Optional[int] = ..., minutes: _Optional[int] = ...) -> None: ...

class Time(_message.Message):
    __slots__ = ("time_of_day", "time_zone")
    TIME_OF_DAY_FIELD_NUMBER: _ClassVar[int]
    TIME_ZONE_FIELD_NUMBER: _ClassVar[int]
    time_of_day: TimeOfDay
    time_zone: TimeZone
    def __init__(self, time_of_day: _Optional[_Union[TimeOfDay, _Mapping]] = ..., time_zone: _Optional[_Union[TimeZone, _Mapping]] = ...) -> None: ...

class TimeZone(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...
