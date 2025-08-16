from dev_observer.api.types import repo_pb2 as _repo_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListRepositoriesResponse(_message.Message):
    __slots__ = ("repos",)
    REPOS_FIELD_NUMBER: _ClassVar[int]
    repos: _containers.RepeatedCompositeFieldContainer[_repo_pb2.GitRepository]
    def __init__(self, repos: _Optional[_Iterable[_Union[_repo_pb2.GitRepository, _Mapping]]] = ...) -> None: ...

class AddRepositoryRequest(_message.Message):
    __slots__ = ("url", "provider")
    URL_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    url: str
    provider: _repo_pb2.GitProvider
    def __init__(self, url: _Optional[str] = ..., provider: _Optional[_Union[_repo_pb2.GitProvider, str]] = ...) -> None: ...

class AddRepositoryResponse(_message.Message):
    __slots__ = ("repo",)
    REPO_FIELD_NUMBER: _ClassVar[int]
    repo: _repo_pb2.GitRepository
    def __init__(self, repo: _Optional[_Union[_repo_pb2.GitRepository, _Mapping]] = ...) -> None: ...

class RescanRepositoryRequest(_message.Message):
    __slots__ = ("research", "skip_summary")
    RESEARCH_FIELD_NUMBER: _ClassVar[int]
    SKIP_SUMMARY_FIELD_NUMBER: _ClassVar[int]
    research: bool
    skip_summary: bool
    def __init__(self, research: bool = ..., skip_summary: bool = ...) -> None: ...

class RescanRepositoryResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetRepositoryResponse(_message.Message):
    __slots__ = ("repo",)
    REPO_FIELD_NUMBER: _ClassVar[int]
    repo: _repo_pb2.GitRepository
    def __init__(self, repo: _Optional[_Union[_repo_pb2.GitRepository, _Mapping]] = ...) -> None: ...

class DeleteRepositoryResponse(_message.Message):
    __slots__ = ("repos",)
    REPOS_FIELD_NUMBER: _ClassVar[int]
    repos: _containers.RepeatedCompositeFieldContainer[_repo_pb2.GitRepository]
    def __init__(self, repos: _Optional[_Iterable[_Union[_repo_pb2.GitRepository, _Mapping]]] = ...) -> None: ...

class FilterRepositoriesRequest(_message.Message):
    __slots__ = ("filter",)
    FILTER_FIELD_NUMBER: _ClassVar[int]
    filter: _repo_pb2.ReposFilter
    def __init__(self, filter: _Optional[_Union[_repo_pb2.ReposFilter, _Mapping]] = ...) -> None: ...

class FilterRepositoriesResponse(_message.Message):
    __slots__ = ("repos",)
    REPOS_FIELD_NUMBER: _ClassVar[int]
    repos: _containers.RepeatedCompositeFieldContainer[_repo_pb2.GitRepository]
    def __init__(self, repos: _Optional[_Iterable[_Union[_repo_pb2.GitRepository, _Mapping]]] = ...) -> None: ...
