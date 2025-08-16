from dev_observer.api.types import sites_pb2 as _sites_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListWebSitesResponse(_message.Message):
    __slots__ = ("sites",)
    SITES_FIELD_NUMBER: _ClassVar[int]
    sites: _containers.RepeatedCompositeFieldContainer[_sites_pb2.WebSite]
    def __init__(self, sites: _Optional[_Iterable[_Union[_sites_pb2.WebSite, _Mapping]]] = ...) -> None: ...

class AddWebSiteRequest(_message.Message):
    __slots__ = ("url", "scan_if_new")
    URL_FIELD_NUMBER: _ClassVar[int]
    SCAN_IF_NEW_FIELD_NUMBER: _ClassVar[int]
    url: str
    scan_if_new: bool
    def __init__(self, url: _Optional[str] = ..., scan_if_new: bool = ...) -> None: ...

class AddWebSiteResponse(_message.Message):
    __slots__ = ("site",)
    SITE_FIELD_NUMBER: _ClassVar[int]
    site: _sites_pb2.WebSite
    def __init__(self, site: _Optional[_Union[_sites_pb2.WebSite, _Mapping]] = ...) -> None: ...

class RescanWebSiteResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetWebSiteResponse(_message.Message):
    __slots__ = ("site",)
    SITE_FIELD_NUMBER: _ClassVar[int]
    site: _sites_pb2.WebSite
    def __init__(self, site: _Optional[_Union[_sites_pb2.WebSite, _Mapping]] = ...) -> None: ...

class DeleteWebSiteResponse(_message.Message):
    __slots__ = ("sites",)
    SITES_FIELD_NUMBER: _ClassVar[int]
    sites: _containers.RepeatedCompositeFieldContainer[_sites_pb2.WebSite]
    def __init__(self, sites: _Optional[_Iterable[_Union[_sites_pb2.WebSite, _Mapping]]] = ...) -> None: ...
