from dev_observer.api.types import repo_pb2 as _repo_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListTokensRequest(_message.Message):
    __slots__ = ("namespace",)
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    def __init__(self, namespace: _Optional[str] = ...) -> None: ...

class ListTokensResponse(_message.Message):
    __slots__ = ("tokens",)
    TOKENS_FIELD_NUMBER: _ClassVar[int]
    tokens: _containers.RepeatedCompositeFieldContainer[_repo_pb2.RepoToken]
    def __init__(self, tokens: _Optional[_Iterable[_Union[_repo_pb2.RepoToken, _Mapping]]] = ...) -> None: ...

class AddTokenRequest(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: _repo_pb2.RepoToken
    def __init__(self, token: _Optional[_Union[_repo_pb2.RepoToken, _Mapping]] = ...) -> None: ...

class AddTokenResponse(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: _repo_pb2.RepoToken
    def __init__(self, token: _Optional[_Union[_repo_pb2.RepoToken, _Mapping]] = ...) -> None: ...

class GetTokenResponse(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: _repo_pb2.RepoToken
    def __init__(self, token: _Optional[_Union[_repo_pb2.RepoToken, _Mapping]] = ...) -> None: ...

class UpdateTokenRequest(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    def __init__(self, token: _Optional[str] = ...) -> None: ...

class UpdateTokenResponse(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: _repo_pb2.RepoToken
    def __init__(self, token: _Optional[_Union[_repo_pb2.RepoToken, _Mapping]] = ...) -> None: ...

class DeleteTokenResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
