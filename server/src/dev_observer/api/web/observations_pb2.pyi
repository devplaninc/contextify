from dev_observer.api.types import observations_pb2 as _observations_pb2
from dev_observer.api.types import processing_pb2 as _processing_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetObservationsResponse(_message.Message):
    __slots__ = ("keys",)
    KEYS_FIELD_NUMBER: _ClassVar[int]
    keys: _containers.RepeatedCompositeFieldContainer[_observations_pb2.ObservationKey]
    def __init__(self, keys: _Optional[_Iterable[_Union[_observations_pb2.ObservationKey, _Mapping]]] = ...) -> None: ...

class GetObservationResponse(_message.Message):
    __slots__ = ("observation",)
    OBSERVATION_FIELD_NUMBER: _ClassVar[int]
    observation: _observations_pb2.Observation
    def __init__(self, observation: _Optional[_Union[_observations_pb2.Observation, _Mapping]] = ...) -> None: ...

class GetProcessingResultsRequest(_message.Message):
    __slots__ = ("from_date", "to_date", "filter")
    FROM_DATE_FIELD_NUMBER: _ClassVar[int]
    TO_DATE_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    from_date: _timestamp_pb2.Timestamp
    to_date: _timestamp_pb2.Timestamp
    filter: _processing_pb2.ProcessingResultFilter
    def __init__(self, from_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., to_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., filter: _Optional[_Union[_processing_pb2.ProcessingResultFilter, _Mapping]] = ...) -> None: ...

class GetProcessingResultsResponse(_message.Message):
    __slots__ = ("results",)
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[_processing_pb2.ProcessingItemResult]
    def __init__(self, results: _Optional[_Iterable[_Union[_processing_pb2.ProcessingItemResult, _Mapping]]] = ...) -> None: ...

class GetProcessingResultResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _processing_pb2.ProcessingItemResult
    def __init__(self, result: _Optional[_Union[_processing_pb2.ProcessingItemResult, _Mapping]] = ...) -> None: ...

class CreateProcessingItemRequest(_message.Message):
    __slots__ = ("key", "process_immediately", "data")
    KEY_FIELD_NUMBER: _ClassVar[int]
    PROCESS_IMMEDIATELY_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    key: _processing_pb2.ProcessingItemKey
    process_immediately: bool
    data: _processing_pb2.ProcessingItemData
    def __init__(self, key: _Optional[_Union[_processing_pb2.ProcessingItemKey, _Mapping]] = ..., process_immediately: bool = ..., data: _Optional[_Union[_processing_pb2.ProcessingItemData, _Mapping]] = ...) -> None: ...

class CreateProcessingItemResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DeleteProcessingItemRequest(_message.Message):
    __slots__ = ("key",)
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: _processing_pb2.ProcessingItemKey
    def __init__(self, key: _Optional[_Union[_processing_pb2.ProcessingItemKey, _Mapping]] = ...) -> None: ...

class DeleteProcessingItemResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetProcessingRunStatusResponse(_message.Message):
    __slots__ = ("result", "item")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    ITEM_FIELD_NUMBER: _ClassVar[int]
    result: _processing_pb2.ProcessingItemResult
    item: _processing_pb2.ProcessingItem
    def __init__(self, result: _Optional[_Union[_processing_pb2.ProcessingItemResult, _Mapping]] = ..., item: _Optional[_Union[_processing_pb2.ProcessingItem, _Mapping]] = ...) -> None: ...

class GetProcessingItemsRequest(_message.Message):
    __slots__ = ("filter",)
    FILTER_FIELD_NUMBER: _ClassVar[int]
    filter: _processing_pb2.ProcessingItemsFilter
    def __init__(self, filter: _Optional[_Union[_processing_pb2.ProcessingItemsFilter, _Mapping]] = ...) -> None: ...

class GetProcessingItemsResponse(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[_processing_pb2.ProcessingItem]
    def __init__(self, items: _Optional[_Iterable[_Union[_processing_pb2.ProcessingItem, _Mapping]]] = ...) -> None: ...
