from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ObservationKey(_message.Message):
    __slots__ = ("kind", "name", "key")
    KIND_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    kind: str
    name: str
    key: str
    def __init__(self, kind: _Optional[str] = ..., name: _Optional[str] = ..., key: _Optional[str] = ...) -> None: ...

class Observation(_message.Message):
    __slots__ = ("key", "content")
    KEY_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    key: ObservationKey
    content: str
    def __init__(self, key: _Optional[_Union[ObservationKey, _Mapping]] = ..., content: _Optional[str] = ...) -> None: ...

class Analyzer(_message.Message):
    __slots__ = ("name", "prompt_prefix", "file_name")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PROMPT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    prompt_prefix: str
    file_name: str
    def __init__(self, name: _Optional[str] = ..., prompt_prefix: _Optional[str] = ..., file_name: _Optional[str] = ...) -> None: ...
