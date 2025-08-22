import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from dev_observer.api.types import ai_pb2 as _ai_pb2
from dev_observer.api.types import observations_pb2 as _observations_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

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
    def __init__(self, last_refresh: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., clone_url: _Optional[str] = ..., size_kb: _Optional[int] = ...) -> None: ...

class GitAppInfo(_message.Message):
    __slots__ = ("last_refresh", "installation_id")
    LAST_REFRESH_FIELD_NUMBER: _ClassVar[int]
    INSTALLATION_ID_FIELD_NUMBER: _ClassVar[int]
    last_refresh: _timestamp_pb2.Timestamp
    installation_id: int
    def __init__(self, last_refresh: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., installation_id: _Optional[int] = ...) -> None: ...

class ReposFilter(_message.Message):
    __slots__ = ("provider", "owner")
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    provider: GitProvider
    owner: str
    def __init__(self, provider: _Optional[_Union[GitProvider, str]] = ..., owner: _Optional[str] = ...) -> None: ...

class CodeResearchMeta(_message.Message):
    __slots__ = ("summary", "created_at", "repo_full_name", "repo_url", "area_title", "dir_key")
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    REPO_FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    REPO_URL_FIELD_NUMBER: _ClassVar[int]
    AREA_TITLE_FIELD_NUMBER: _ClassVar[int]
    DIR_KEY_FIELD_NUMBER: _ClassVar[int]
    summary: str
    created_at: _timestamp_pb2.Timestamp
    repo_full_name: str
    repo_url: str
    area_title: str
    dir_key: _observations_pb2.ObservationKey
    def __init__(self, summary: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., repo_full_name: _Optional[str] = ..., repo_url: _Optional[str] = ..., area_title: _Optional[str] = ..., dir_key: _Optional[_Union[_observations_pb2.ObservationKey, _Mapping]] = ...) -> None: ...

class CodeResearchAreaMeta(_message.Message):
    __slots__ = ("research_key", "meta")
    RESEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    research_key: _observations_pb2.ObservationKey
    meta: CodeResearchMeta
    def __init__(self, research_key: _Optional[_Union[_observations_pb2.ObservationKey, _Mapping]] = ..., meta: _Optional[_Union[CodeResearchMeta, _Mapping]] = ...) -> None: ...

class CodeResearchOrganizationMeta(_message.Message):
    __slots__ = ("area_metas",)
    AREA_METAS_FIELD_NUMBER: _ClassVar[int]
    area_metas: _containers.RepeatedCompositeFieldContainer[CodeResearchAreaMeta]
    def __init__(self, area_metas: _Optional[_Iterable[_Union[CodeResearchAreaMeta, _Mapping]]] = ...) -> None: ...

class ResearchLog(_message.Message):
    __slots__ = ("items", "started_at", "finished_at", "total_usage")
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_USAGE_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[ResearchLogItem]
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    total_usage: _ai_pb2.UsageMetadata
    def __init__(self, items: _Optional[_Iterable[_Union[ResearchLogItem, _Mapping]]] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., total_usage: _Optional[_Union[_ai_pb2.UsageMetadata, _Mapping]] = ...) -> None: ...

class ResearchLogItem(_message.Message):
    __slots__ = ("observations", "tool_calls", "started_at", "finished_at", "summary", "usage")
    OBSERVATIONS_FIELD_NUMBER: _ClassVar[int]
    TOOL_CALLS_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    observations: str
    tool_calls: _containers.RepeatedCompositeFieldContainer[ToolCallResult]
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    summary: str
    usage: _ai_pb2.UsageMetadata
    def __init__(self, observations: _Optional[str] = ..., tool_calls: _Optional[_Iterable[_Union[ToolCallResult, _Mapping]]] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., summary: _Optional[str] = ..., usage: _Optional[_Union[_ai_pb2.UsageMetadata, _Mapping]] = ...) -> None: ...

class ToolCallResult(_message.Message):
    __slots__ = ("requested_tool_call", "result", "status")
    class ToolCallStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNPROCESSED: _ClassVar[ToolCallResult.ToolCallStatus]
        SUCCESS: _ClassVar[ToolCallResult.ToolCallStatus]
        FAILURE: _ClassVar[ToolCallResult.ToolCallStatus]
    UNPROCESSED: ToolCallResult.ToolCallStatus
    SUCCESS: ToolCallResult.ToolCallStatus
    FAILURE: ToolCallResult.ToolCallStatus
    REQUESTED_TOOL_CALL_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    requested_tool_call: str
    result: str
    status: ToolCallResult.ToolCallStatus
    def __init__(self, requested_tool_call: _Optional[str] = ..., result: _Optional[str] = ..., status: _Optional[_Union[ToolCallResult.ToolCallStatus, str]] = ...) -> None: ...
