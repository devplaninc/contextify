from google.protobuf import timestamp_pb2 as _timestamp_pb2
from dev_observer.api.types import observations_pb2 as _observations_pb2
from dev_observer.api.types import schedule_pb2 as _schedule_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProcessingItemKey(_message.Message):
    __slots__ = ("github_repo_id", "website_url", "request_id", "periodic_aggregation_id")
    GITHUB_REPO_ID_FIELD_NUMBER: _ClassVar[int]
    WEBSITE_URL_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    PERIODIC_AGGREGATION_ID_FIELD_NUMBER: _ClassVar[int]
    github_repo_id: str
    website_url: str
    request_id: str
    periodic_aggregation_id: str
    def __init__(self, github_repo_id: _Optional[str] = ..., website_url: _Optional[str] = ..., request_id: _Optional[str] = ..., periodic_aggregation_id: _Optional[str] = ...) -> None: ...

class ProcessingItem(_message.Message):
    __slots__ = ("key", "next_processing", "last_processed", "last_error", "no_processing", "processing_started_at", "data")
    KEY_FIELD_NUMBER: _ClassVar[int]
    NEXT_PROCESSING_FIELD_NUMBER: _ClassVar[int]
    LAST_PROCESSED_FIELD_NUMBER: _ClassVar[int]
    LAST_ERROR_FIELD_NUMBER: _ClassVar[int]
    NO_PROCESSING_FIELD_NUMBER: _ClassVar[int]
    PROCESSING_STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    key: ProcessingItemKey
    next_processing: _timestamp_pb2.Timestamp
    last_processed: _timestamp_pb2.Timestamp
    last_error: str
    no_processing: bool
    processing_started_at: _timestamp_pb2.Timestamp
    data: ProcessingItemData
    def __init__(self, key: _Optional[_Union[ProcessingItemKey, _Mapping]] = ..., next_processing: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_processed: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_error: _Optional[str] = ..., no_processing: bool = ..., processing_started_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., data: _Optional[_Union[ProcessingItemData, _Mapping]] = ...) -> None: ...

class PeriodicAggregation(_message.Message):
    __slots__ = ("params", "schedule")
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_FIELD_NUMBER: _ClassVar[int]
    params: AggregatedSummaryParams
    schedule: _schedule_pb2.Schedule
    def __init__(self, params: _Optional[_Union[AggregatedSummaryParams, _Mapping]] = ..., schedule: _Optional[_Union[_schedule_pb2.Schedule, _Mapping]] = ...) -> None: ...

class AggregatedSummaryParams(_message.Message):
    __slots__ = ("look_back_days", "end_date", "target")
    class Target(_message.Message):
        __slots__ = ("git_repo_ids",)
        GIT_REPO_IDS_FIELD_NUMBER: _ClassVar[int]
        git_repo_ids: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, git_repo_ids: _Optional[_Iterable[str]] = ...) -> None: ...
    LOOK_BACK_DAYS_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    look_back_days: int
    end_date: _timestamp_pb2.Timestamp
    target: AggregatedSummaryParams.Target
    def __init__(self, look_back_days: _Optional[int] = ..., end_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., target: _Optional[_Union[AggregatedSummaryParams.Target, _Mapping]] = ...) -> None: ...

class ProcessingRequest(_message.Message):
    __slots__ = ("git_changes",)
    GIT_CHANGES_FIELD_NUMBER: _ClassVar[int]
    git_changes: ProcessGitChangesRequest
    def __init__(self, git_changes: _Optional[_Union[ProcessGitChangesRequest, _Mapping]] = ...) -> None: ...

class ProcessGitChangesRequest(_message.Message):
    __slots__ = ("git_repo_id", "look_back_days")
    GIT_REPO_ID_FIELD_NUMBER: _ClassVar[int]
    LOOK_BACK_DAYS_FIELD_NUMBER: _ClassVar[int]
    git_repo_id: str
    look_back_days: int
    def __init__(self, git_repo_id: _Optional[str] = ..., look_back_days: _Optional[int] = ...) -> None: ...

class ProcessingItemResult(_message.Message):
    __slots__ = ("id", "key", "error_message", "created_at", "data", "result_data")
    ID_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    RESULT_DATA_FIELD_NUMBER: _ClassVar[int]
    id: str
    key: ProcessingItemKey
    error_message: str
    created_at: _timestamp_pb2.Timestamp
    data: ProcessingItemData
    result_data: ProcessingItemResultData
    def __init__(self, id: _Optional[str] = ..., key: _Optional[_Union[ProcessingItemKey, _Mapping]] = ..., error_message: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., data: _Optional[_Union[ProcessingItemData, _Mapping]] = ..., result_data: _Optional[_Union[ProcessingItemResultData, _Mapping]] = ...) -> None: ...

class RepoObservation(_message.Message):
    __slots__ = ("repo_id", "observations")
    REPO_ID_FIELD_NUMBER: _ClassVar[int]
    OBSERVATIONS_FIELD_NUMBER: _ClassVar[int]
    repo_id: str
    observations: _containers.RepeatedCompositeFieldContainer[_observations_pb2.ObservationKey]
    def __init__(self, repo_id: _Optional[str] = ..., observations: _Optional[_Iterable[_Union[_observations_pb2.ObservationKey, _Mapping]]] = ...) -> None: ...

class PeriodicAggregationResult(_message.Message):
    __slots__ = ("repo_observations",)
    REPO_OBSERVATIONS_FIELD_NUMBER: _ClassVar[int]
    repo_observations: _containers.RepeatedCompositeFieldContainer[RepoObservation]
    def __init__(self, repo_observations: _Optional[_Iterable[_Union[RepoObservation, _Mapping]]] = ...) -> None: ...

class ProcessingItemData(_message.Message):
    __slots__ = ("reference_id", "namespace", "created_by", "request", "periodic_aggregation")
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    PERIODIC_AGGREGATION_FIELD_NUMBER: _ClassVar[int]
    reference_id: str
    namespace: str
    created_by: str
    request: ProcessingRequest
    periodic_aggregation: PeriodicAggregation
    def __init__(self, reference_id: _Optional[str] = ..., namespace: _Optional[str] = ..., created_by: _Optional[str] = ..., request: _Optional[_Union[ProcessingRequest, _Mapping]] = ..., periodic_aggregation: _Optional[_Union[PeriodicAggregation, _Mapping]] = ...) -> None: ...

class ProcessingItemResultData(_message.Message):
    __slots__ = ("observations", "periodic_aggregation")
    OBSERVATIONS_FIELD_NUMBER: _ClassVar[int]
    PERIODIC_AGGREGATION_FIELD_NUMBER: _ClassVar[int]
    observations: _containers.RepeatedCompositeFieldContainer[_observations_pb2.ObservationKey]
    periodic_aggregation: PeriodicAggregationResult
    def __init__(self, observations: _Optional[_Iterable[_Union[_observations_pb2.ObservationKey, _Mapping]]] = ..., periodic_aggregation: _Optional[_Union[PeriodicAggregationResult, _Mapping]] = ...) -> None: ...

class ProcessingResultFilter(_message.Message):
    __slots__ = ("namespace", "reference_id", "request_type", "keys")
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_TYPE_FIELD_NUMBER: _ClassVar[int]
    KEYS_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    reference_id: str
    request_type: str
    keys: _containers.RepeatedCompositeFieldContainer[ProcessingItemKey]
    def __init__(self, namespace: _Optional[str] = ..., reference_id: _Optional[str] = ..., request_type: _Optional[str] = ..., keys: _Optional[_Iterable[_Union[ProcessingItemKey, _Mapping]]] = ...) -> None: ...

class ProcessingItemsFilter(_message.Message):
    __slots__ = ("namespace", "reference_id", "request_type", "keys")
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_TYPE_FIELD_NUMBER: _ClassVar[int]
    KEYS_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    reference_id: str
    request_type: str
    keys: _containers.RepeatedCompositeFieldContainer[ProcessingItemKey]
    def __init__(self, namespace: _Optional[str] = ..., reference_id: _Optional[str] = ..., request_type: _Optional[str] = ..., keys: _Optional[_Iterable[_Union[ProcessingItemKey, _Mapping]]] = ...) -> None: ...
