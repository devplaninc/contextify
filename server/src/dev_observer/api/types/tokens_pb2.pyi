import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AuthTokenProvider(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN: _ClassVar[AuthTokenProvider]
    BIT_BUCKET: _ClassVar[AuthTokenProvider]
    JIRA: _ClassVar[AuthTokenProvider]
UNKNOWN: AuthTokenProvider
BIT_BUCKET: AuthTokenProvider
JIRA: AuthTokenProvider

class AuthToken(_message.Message):
    __slots__ = ("id", "namespace", "provider", "workspace", "repo", "system", "token", "expires_at", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    REPO_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    namespace: str
    provider: AuthTokenProvider
    workspace: str
    repo: str
    system: bool
    token: str
    expires_at: _timestamp_pb2.Timestamp
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., namespace: _Optional[str] = ..., provider: _Optional[_Union[AuthTokenProvider, str]] = ..., workspace: _Optional[str] = ..., repo: _Optional[str] = ..., system: bool = ..., token: _Optional[str] = ..., expires_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class TokensFilter(_message.Message):
    __slots__ = ("namespace", "workspace", "provider")
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    workspace: str
    provider: AuthTokenProvider
    def __init__(self, namespace: _Optional[str] = ..., workspace: _Optional[str] = ..., provider: _Optional[_Union[AuthTokenProvider, str]] = ...) -> None: ...
