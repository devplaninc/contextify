import abc
import asyncio
import datetime
import logging
import uuid
from abc import abstractmethod
from typing import Optional, Callable, MutableSequence, List, Sequence

from google.protobuf import timestamp

from dev_observer.api.storage.local_pb2 import LocalStorageData
from dev_observer.api.types.config_pb2 import GlobalConfig
from dev_observer.api.types.processing_pb2 import ProcessingItem, ProcessingItemKey, ProcessingItemResult, \
    ProcessingResultFilter, ProcessingItemsFilter, ProcessingItemData
from dev_observer.api.types.repo_pb2 import GitRepository, GitProperties
from dev_observer.api.types.sites_pb2 import WebSite
from dev_observer.common.schedule import pb_to_datetime
from dev_observer.storage.provider import StorageProvider, AddWebSiteData
from dev_observer.util import Clock, RealClock

_log = logging.getLogger(__name__)

_lock = asyncio.Lock()


class SingleBlobStorageProvider(abc.ABC, StorageProvider):
    _clock: Clock

    def __init__(self, clock: Clock = RealClock()):
        self._clock = clock

    async def get_git_repos(self) -> MutableSequence[GitRepository]:
        return self._get().git_repos

    async def get_git_repo(self, repo_id: str) -> Optional[GitRepository]:
        for r in self._get().git_repos:
            if r.id == repo_id:
                return r
        return None

    async def delete_git_repo(self, repo_id: str):
        def up(d: LocalStorageData):
            new_repos = [r for r in d.git_repos if r.id != repo_id]
            d.ClearField("git_repos")
            d.git_repos.extend(new_repos)

        await self._update(up)

    async def add_git_repo(self, repo: GitRepository) -> GitRepository:
        if not repo.id or len(repo.id) == 0:
            repo.id = f"{uuid.uuid4()}"

        def up(d: LocalStorageData):
            if repo.id in [r.id for r in self._get().git_repos]:
                return
            d.git_repos.append(repo)

        await self._update(up)
        return repo

    async def update_repo_properties(self, id: str, properties: GitProperties) -> GitRepository:
        def up(d: LocalStorageData):
            for r in d.git_repos:
                if r.id == id:
                    r.properties.CopyFrom(properties)
                    return
            raise ValueError(f"Repository with id {id} not found")

        await self._update(up)
        return await self.get_git_repo(id)

    async def get_web_sites(self) -> MutableSequence[WebSite]:
        return self._get().web_sites

    async def get_web_site(self, site_id: str) -> Optional[WebSite]:
        for s in self._get().web_sites:
            if s.id == site_id:
                return s
        return None

    async def delete_web_site(self, site_id: str):
        def up(d: LocalStorageData):
            new_sites = [s for s in d.web_sites if s.id != site_id]
            d.ClearField("web_sites")
            d.web_sites.extend(new_sites)

        await self._update(up)

    async def add_web_site(self, site: WebSite) -> AddWebSiteData:
        if not site.id or len(site.id) == 0:
            site.id = f"{uuid.uuid4()}"
        initial_id = site.id

        def up(d: LocalStorageData):
            if site.url in [s.url for s in self._get().web_sites]:
                return
            d.web_sites.append(site)
            if site.url not in [i.key.website_url for i in self._get().processing_items]:
                d.processing_items.append(ProcessingItem(
                    key=ProcessingItemKey(website_url=site.url),
                    next_processing=self._clock.now(),
                ))

        await self._update(up)
        async with _lock:
            for s in self._get().web_sites:
                if s.url == site.url:
                    return AddWebSiteData(s, created=initial_id == s.id)

        raise ValueError(f"Site with url {site.url} not found after creation")

    async def next_processing_item(self) -> Optional[ProcessingItem]:
        now = self._clock.now()
        items = [i for i in self._get().processing_items if
                 i.HasField("next_processing") and pb_to_datetime(i.next_processing) < now]
        if len(items) == 0:
            return None
        items.sort(key=lambda item: pb_to_datetime(item.next_processing))
        return items[0]

    async def get_processing_items(self, filter: ProcessingItemsFilter) -> Sequence[ProcessingItem]:
        items = []

        for item in self._get().processing_items:
            if filter.namespace and filter.namespace != item.data.namespace:
                continue
            if filter.reference_id and filter.reference_id != item.data.reference_id:
                continue
            if filter.request_type:
                is_req = item.HasField("data") and item.data.WhichOneof("type") == "request"
                if not is_req or filter.request_type != item.data.request.WhichOneof("type"):
                    continue

            items.append(item)

        return items

    async def get_processing_item(self, key: ProcessingItemKey) -> Optional[ProcessingItem]:
        for i in self._get().processing_items:
            if i.key == key:
                return i
        return None

    async def set_next_processing_time(self, key: ProcessingItemKey, next_time: Optional[datetime.datetime],
                                       error: Optional[str] = None,
                                       processing_started_at: Optional[datetime.datetime] = None,
                                       ):
        def up(d: LocalStorageData):
            found = False
            for i in d.processing_items:
                if i.key == key:
                    found = True
                    if next_time is None:
                        i.ClearField("next_processing")
                    else:
                        i.next_processing.CopyFrom(timestamp.from_milliseconds(int(next_time.timestamp() * 1000)))
                    i.last_error = error or ""
                    if processing_started_at:
                        i.processing_started_at = processing_started_at

            if not found:
                d.processing_items.append(ProcessingItem(key=key, next_processing=next_time, last_error=error))

        await self._update(up)

    async def upsert_processing_item(self, item: ProcessingItem):
        def up(d: LocalStorageData):
            if item.key in [i.key for i in d.processing_items]:
                new_items = [item if i.key == item.key else i for i in d.processing_items]
                d.processing_items.clear()
                d.processing_items.extend(new_items)
            else:
                d.processing_items.append(item)

        await self._update(up)

    async def get_global_config(self) -> GlobalConfig:
        return self._get().global_config

    async def set_global_config(self, config: GlobalConfig) -> GlobalConfig:
        def up(d: LocalStorageData):
            d.global_config.CopyFrom(config)

        data = await self._update(up)
        return data.global_config

    async def _update(self, updater: Callable[[LocalStorageData], None]) -> LocalStorageData:
        async with _lock:
            data = self._get()
            updater(data)
            self._store(data)
            return self._get()

    async def create_processing_time(self, key: ProcessingItemKey,
                                     data: Optional[ProcessingItemData] = None,
                                     next_time: Optional[datetime.datetime] = None):
        def up(d: LocalStorageData):
            for item in d.processing_items:
                if item.key == key:
                    return

            new_item = ProcessingItem(key=key, data=data)
            if next_time is not None:
                new_item.next_processing.CopyFrom(timestamp.from_milliseconds(int(next_time.timestamp() * 1000)))

            d.processing_items.append(new_item)

        await self._update(up)

    async def update_processing_item(
            self,
            key: ProcessingItemKey,
            updater: Callable[[ProcessingItem], ProcessingItem],
            next_time: Optional[datetime.datetime] = None,
    ):
        def up(d: LocalStorageData):
            for item in d.processing_items:
                if item.key == key:
                    updater(item)
                    if next_time:
                        item.next_processing.CopyFrom(timestamp.from_milliseconds(int(next_time.timestamp() * 1000)))
                    return
            raise ValueError(f"Processing item with key {key} not found")

        await self._update(up)

    async def delete_processing_item(self, key: ProcessingItemKey):
        def up(d: LocalStorageData):
            new_items = [item for item in d.processing_items if item.key != key]
            d.ClearField("processing_items")
            d.processing_items.extend(new_items)

        await self._update(up)

    async def set_processing_error(self, key: ProcessingItemKey, error: Optional[str] = None):
        def up(d: LocalStorageData):
            for item in d.processing_items:
                if item.key == key:
                    item.last_error = error if error is not None else ""
                    return
            raise ValueError(f"Processing item with key {key} not found")

        await self._update(up)

    async def add_processing_result(self, item: ProcessingItemResult) -> str:
        if not item.id or len(item.id) == 0:
            item.id = f"{uuid.uuid4()}"

        def up(d: LocalStorageData):
            # Set created_at if not already set
            if not item.HasField("created_at"):
                item.created_at.CopyFrom(timestamp.from_milliseconds(int(self._clock.now().timestamp() * 1000)))

            d.processing_results.append(item)

        await self._update(up)
        return item.id

    async def get_processing_results(
            self,
            from_date: datetime.datetime, to_date: datetime.datetime, filter: ProcessingResultFilter
    ) -> List[ProcessingItemResult]:
        results = []

        if from_date.tzinfo is None:
            from_date = from_date.replace(tzinfo=datetime.timezone.utc)
        if to_date.tzinfo is None:
            to_date = to_date.replace(tzinfo=datetime.timezone.utc)

        for result in self._get().processing_results:
            if filter.namespace and filter.namespace != result.data.namespace:
                continue
            if filter.reference_id and filter.reference_id != result.data.reference_id:
                continue
            is_req = result.HasField("data") and result.data.WhichOneof("type") == "request"
            if filter.request_type and (not is_req
                                        or filter.request_type != result.data.request.WhichOneof("type")):
                continue
            created_at = pb_to_datetime(result.created_at)
            if from_date <= created_at <= to_date:
                results.append(result)

        # Sort by created_at descending (most recent first)
        results.sort(key=lambda r: pb_to_datetime(r.created_at), reverse=True)
        return results

    async def get_processing_item(self, key: ProcessingItemKey) -> Optional[ProcessingItem]:
        for item in self._get().processing_items:
            if item.key == key:
                return item
        return None

    async def get_processing_result(self, result_id: str) -> Optional[ProcessingItemResult]:
        for result in self._get().processing_results:
            if result.id == result_id:
                return result
        return None

    @abstractmethod
    def _get(self) -> LocalStorageData:
        ...

    @abstractmethod
    def _store(self, data: LocalStorageData):
        ...
