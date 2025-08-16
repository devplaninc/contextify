from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PromptConfig(_message.Message):
    __slots__ = ("model",)
    MODEL_FIELD_NUMBER: _ClassVar[int]
    model: ModelConfig
    def __init__(self, model: _Optional[_Union[ModelConfig, _Mapping]] = ...) -> None: ...

class ModelConfig(_message.Message):
    __slots__ = ("provider", "model_name", "temperature")
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    provider: str
    model_name: str
    temperature: float
    def __init__(self, provider: _Optional[str] = ..., model_name: _Optional[str] = ..., temperature: _Optional[float] = ...) -> None: ...

class SystemMessage(_message.Message):
    __slots__ = ("text",)
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class UserMessage(_message.Message):
    __slots__ = ("text", "image_urls")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    IMAGE_URLS_FIELD_NUMBER: _ClassVar[int]
    text: str
    image_urls: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, text: _Optional[str] = ..., image_urls: _Optional[_Iterable[str]] = ...) -> None: ...

class PromptTemplate(_message.Message):
    __slots__ = ("system", "user", "config")
    SYSTEM_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    system: SystemMessage
    user: UserMessage
    config: PromptConfig
    def __init__(self, system: _Optional[_Union[SystemMessage, _Mapping]] = ..., user: _Optional[_Union[UserMessage, _Mapping]] = ..., config: _Optional[_Union[PromptConfig, _Mapping]] = ...) -> None: ...
