from dev_observer.api.types import config_pb2 as _config_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetGlobalConfigResponse(_message.Message):
    __slots__ = ("config",)
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    config: _config_pb2.GlobalConfig
    def __init__(self, config: _Optional[_Union[_config_pb2.GlobalConfig, _Mapping]] = ...) -> None: ...

class UpdateGlobalConfigRequest(_message.Message):
    __slots__ = ("config",)
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    config: _config_pb2.GlobalConfig
    def __init__(self, config: _Optional[_Union[_config_pb2.GlobalConfig, _Mapping]] = ...) -> None: ...

class UpdateGlobalConfigResponse(_message.Message):
    __slots__ = ("config",)
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    config: _config_pb2.GlobalConfig
    def __init__(self, config: _Optional[_Union[_config_pb2.GlobalConfig, _Mapping]] = ...) -> None: ...

class GetUserManagementStatusResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _config_pb2.UserManagementStatus
    def __init__(self, status: _Optional[_Union[_config_pb2.UserManagementStatus, _Mapping]] = ...) -> None: ...
