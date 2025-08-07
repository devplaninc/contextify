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
    __slots__ = ("id", "name", "full_name", "url", "description", "provider", "properties", "integration_info")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    INTEGRATION_INFO_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    full_name: str
    url: str
    description: str
    provider: GitProvider
    properties: GitProperties
    integration_info: GitIntegrationInfo
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., full_name: _Optional[str] = ..., url: _Optional[str] = ..., description: _Optional[str] = ..., provider: _Optional[_Union[GitProvider, str]] = ..., properties: _Optional[_Union[GitProperties, _Mapping]] = ..., integration_info: _Optional[_Union[GitIntegrationInfo, _Mapping]] = ...) -> None: ...

class GitProperties(_message.Message):
    __slots__ = ("app_info", "meta")
    APP_INFO_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    app_info: GitAppInfo
    meta: GitMeta
    def __init__(self, app_info: _Optional[_Union[GitAppInfo, _Mapping]] = ..., meta: _Optional[_Union[GitMeta, _Mapping]] = ...) -> None: ...

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

class GitIntegrationInfo(_message.Message):
    __slots__ = ("github", "bitbucket")
    GITHUB_FIELD_NUMBER: _ClassVar[int]
    BITBUCKET_FIELD_NUMBER: _ClassVar[int]
    github: GitHubIntegrationInfo
    bitbucket: BitBucketIntegrationInfo
    def __init__(self, github: _Optional[_Union[GitHubIntegrationInfo, _Mapping]] = ..., bitbucket: _Optional[_Union[BitBucketIntegrationInfo, _Mapping]] = ...) -> None: ...

class GitHubIntegrationInfo(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BitBucketIntegrationInfo(_message.Message):
    __slots__ = ("token_id",)
    TOKEN_ID_FIELD_NUMBER: _ClassVar[int]
    token_id: str
    def __init__(self, token_id: _Optional[str] = ...) -> None: ...

class RepoToken(_message.Message):
    __slots__ = ("id", "namespace", "provider", "workspace", "repo", "system", "expires_at", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    REPO_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    namespace: str
    provider: GitProvider
    workspace: str
    repo: str
    system: bool
    expires_at: _timestamp_pb2.Timestamp
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., namespace: _Optional[str] = ..., provider: _Optional[_Union[GitProvider, str]] = ..., workspace: _Optional[str] = ..., repo: _Optional[str] = ..., system: bool = ..., expires_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
