from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GitProvider(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GITHUB: _ClassVar[GitProvider]
    BIT_BUCKET: _ClassVar[GitProvider]
GITHUB: GitProvider
BIT_BUCKET: GitProvider

class GitRepository(_message.Message):
    __slots__ = ("id", "name", "full_name", "url", "description", "provider", "properties")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    full_name: str
    url: str
    description: str
    provider: GitProvider
    properties: GitProperties
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., full_name: _Optional[str] = ..., url: _Optional[str] = ..., description: _Optional[str] = ..., provider: _Optional[_Union[GitProvider, str]] = ..., properties: _Optional[_Union[GitProperties, _Mapping]] = ...) -> None: ...

class GitProperties(_message.Message):
    __slots__ = ("app_info", "meta", "bit_bucket_info")
    APP_INFO_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    BIT_BUCKET_INFO_FIELD_NUMBER: _ClassVar[int]
    app_info: GitAppInfo
    meta: GitMeta
    bit_bucket_info: BitBucketInfo
    def __init__(self, app_info: _Optional[_Union[GitAppInfo, _Mapping]] = ..., meta: _Optional[_Union[GitMeta, _Mapping]] = ..., bit_bucket_info: _Optional[_Union[BitBucketInfo, _Mapping]] = ...) -> None: ...

class BitBucketInfo(_message.Message):
    __slots__ = ("workspace_uuid",)
    WORKSPACE_UUID_FIELD_NUMBER: _ClassVar[int]
    workspace_uuid: str
    def __init__(self, workspace_uuid: _Optional[str] = ...) -> None: ...

class GitMeta(_message.Message):
    __slots__ = ("last_refresh", "clone_url", "size_kb")
    LAST_REFRESH_FIELD_NUMBER: _ClassVar[int]
    CLONE_URL_FIELD_NUMBER: _ClassVar[int]
    SIZE_KB_FIELD_NUMBER: _ClassVar[int]
    last_refresh: _timestamp_pb2.Timestamp
    clone_url: str
    size_kb: int
    def __init__(self, last_refresh: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., clone_url: _Optional[str] = ..., size_kb: _Optional[int] = ...) -> None: ...

class GitAppInfo(_message.Message):
    __slots__ = ("last_refresh", "installation_id")
    LAST_REFRESH_FIELD_NUMBER: _ClassVar[int]
    INSTALLATION_ID_FIELD_NUMBER: _ClassVar[int]
    last_refresh: _timestamp_pb2.Timestamp
    installation_id: int
    def __init__(self, last_refresh: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., installation_id: _Optional[int] = ...) -> None: ...

class ReposFilter(_message.Message):
    __slots__ = ("provider", "owner")
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    provider: GitProvider
    owner: str
    def __init__(self, provider: _Optional[_Union[GitProvider, str]] = ..., owner: _Optional[str] = ...) -> None: ...

class CodeResearchMeta(_message.Message):
    __slots__ = ("summary", "created_at")
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    summary: str
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, summary: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
