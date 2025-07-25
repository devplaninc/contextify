from google.protobuf import timestamp_pb2 as _timestamp_pb2
from dev_observer.api.types import observations_pb2 as _observations_pb2
from dev_observer.api.types import schedule_pb2 as _schedule_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProcessingItemKey(_message.Message):
    __slots__ = ("github_repo_id", "website_url", "request_id", "periodic_processing_id")
    GITHUB_REPO_ID_FIELD_NUMBER: _ClassVar[int]
    WEBSITE_URL_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    PERIODIC_PROCESSING_ID_FIELD_NUMBER: _ClassVar[int]
    github_repo_id: str
    website_url: str
    request_id: str
    periodic_processing_id: str
    def __init__(self, github_repo_id: _Optional[str] = ..., website_url: _Optional[str] = ..., request_id: _Optional[str] = ..., periodic_processing_id: _Optional[str] = ...) -> None: ...

class ProcessingItem(_message.Message):
    __slots__ = ("key", "next_processing", "last_processed", "last_error", "no_processing", "request", "processing_started_at", "periodic_processing")
    KEY_FIELD_NUMBER: _ClassVar[int]
    NEXT_PROCESSING_FIELD_NUMBER: _ClassVar[int]
    LAST_PROCESSED_FIELD_NUMBER: _ClassVar[int]
    LAST_ERROR_FIELD_NUMBER: _ClassVar[int]
    NO_PROCESSING_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    PROCESSING_STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    PERIODIC_PROCESSING_FIELD_NUMBER: _ClassVar[int]
    key: ProcessingItemKey
    next_processing: _timestamp_pb2.Timestamp
    last_processed: _timestamp_pb2.Timestamp
    last_error: str
    no_processing: bool
    request: ProcessingRequest
    processing_started_at: _timestamp_pb2.Timestamp
    periodic_processing: PeriodicProcessing
    def __init__(self, key: _Optional[_Union[ProcessingItemKey, _Mapping]] = ..., next_processing: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_processed: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_error: _Optional[str] = ..., no_processing: bool = ..., request: _Optional[_Union[ProcessingRequest, _Mapping]] = ..., processing_started_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., periodic_processing: _Optional[_Union[PeriodicProcessing, _Mapping]] = ...) -> None: ...

class PeriodicProcessing(_message.Message):
    __slots__ = ("folder_prefix", "look_back_days", "end_date", "target", "schedule")
    class Target(_message.Message):
        __slots__ = ("git_repo_ids",)
        GIT_REPO_IDS_FIELD_NUMBER: _ClassVar[int]
        git_repo_ids: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, git_repo_ids: _Optional[_Iterable[str]] = ...) -> None: ...
    FOLDER_PREFIX_FIELD_NUMBER: _ClassVar[int]
    LOOK_BACK_DAYS_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_FIELD_NUMBER: _ClassVar[int]
    folder_prefix: str
    look_back_days: int
    end_date: _timestamp_pb2.Timestamp
    target: PeriodicProcessing.Target
    schedule: _schedule_pb2.Schedule
    def __init__(self, folder_prefix: _Optional[str] = ..., look_back_days: _Optional[int] = ..., end_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., target: _Optional[_Union[PeriodicProcessing.Target, _Mapping]] = ..., schedule: _Optional[_Union[_schedule_pb2.Schedule, _Mapping]] = ...) -> None: ...

class ProcessingRequest(_message.Message):
    __slots__ = ("created_by", "namespace", "reference_id", "git_changes")
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    GIT_CHANGES_FIELD_NUMBER: _ClassVar[int]
    created_by: str
    namespace: str
    reference_id: str
    git_changes: ProcessGitChangesRequest
    def __init__(self, created_by: _Optional[str] = ..., namespace: _Optional[str] = ..., reference_id: _Optional[str] = ..., git_changes: _Optional[_Union[ProcessGitChangesRequest, _Mapping]] = ...) -> None: ...

class ProcessGitChangesRequest(_message.Message):
    __slots__ = ("git_repo_id", "look_back_days")
    GIT_REPO_ID_FIELD_NUMBER: _ClassVar[int]
    LOOK_BACK_DAYS_FIELD_NUMBER: _ClassVar[int]
    git_repo_id: str
    look_back_days: int
    def __init__(self, git_repo_id: _Optional[str] = ..., look_back_days: _Optional[int] = ...) -> None: ...

class ProcessingItemResult(_message.Message):
    __slots__ = ("id", "key", "observations", "error_message", "created_at", "request", "periodic_processing")
    ID_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    OBSERVATIONS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    PERIODIC_PROCESSING_FIELD_NUMBER: _ClassVar[int]
    id: str
    key: ProcessingItemKey
    observations: _containers.RepeatedCompositeFieldContainer[_observations_pb2.ObservationKey]
    error_message: str
    created_at: _timestamp_pb2.Timestamp
    request: ProcessingRequest
    periodic_processing: PeriodicProcessing
    def __init__(self, id: _Optional[str] = ..., key: _Optional[_Union[ProcessingItemKey, _Mapping]] = ..., observations: _Optional[_Iterable[_Union[_observations_pb2.ObservationKey, _Mapping]]] = ..., error_message: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., request: _Optional[_Union[ProcessingRequest, _Mapping]] = ..., periodic_processing: _Optional[_Union[PeriodicProcessing, _Mapping]] = ...) -> None: ...

class ProcessingResultFilter(_message.Message):
    __slots__ = ("namespace", "reference_id", "request_type")
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_TYPE_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    reference_id: str
    request_type: str
    def __init__(self, namespace: _Optional[str] = ..., reference_id: _Optional[str] = ..., request_type: _Optional[str] = ...) -> None: ...

class ProcessingItemsFilter(_message.Message):
    __slots__ = ("namespace", "reference_id", "request_type")
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_TYPE_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    reference_id: str
    request_type: str
    def __init__(self, namespace: _Optional[str] = ..., reference_id: _Optional[str] = ..., request_type: _Optional[str] = ...) -> None: ...
