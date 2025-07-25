import datetime
import uuid
from typing import Optional, MutableSequence, List, Sequence, Callable

from google.protobuf import json_format
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession

from dev_observer.api.types.config_pb2 import GlobalConfig
from dev_observer.api.types.processing_pb2 import ProcessingItem, ProcessingItemKey, \
    ProcessingItemResult, ProcessingRequest, ProcessingResultFilter, ProcessingItemsFilter
from dev_observer.api.types.repo_pb2 import GitHubRepository, GitProperties
from dev_observer.api.types.schedule_pb2 import Schedule
from dev_observer.api.types.sites_pb2 import WebSite
from dev_observer.storage.postgresql.model import GitRepoEntity, ProcessingItemEntity, GlobalConfigEntity, \
    WebsiteEntity, ProcessingItemResultEntity
from dev_observer.storage.provider import StorageProvider, AddWebSiteData
from dev_observer.util import parse_json_pb, pb_to_json, Clock, RealClock


class PostgresqlStorageProvider(StorageProvider):
    _engine: AsyncEngine
    _clock: Clock

    def __init__(self, url: str, echo: bool = False, clock: Clock = RealClock()):
        self._engine = create_async_engine(url, echo=echo)
        self._clock = clock

    async def get_github_repos(self) -> MutableSequence[GitHubRepository]:
        async with AsyncSession(self._engine) as session:
            entities = await session.execute(select(GitRepoEntity))
            return [_to_repo(e[0]) for e in entities.all()]

    async def get_github_repo(self, repo_id: str) -> Optional[GitHubRepository]:
        async with AsyncSession(self._engine) as session:
            return _to_optional_repo(await session.get(GitRepoEntity, repo_id))

    async def get_github_repo_by_full_name(self, full_name: str) -> Optional[GitHubRepository]:
        async with AsyncSession(self._engine) as session:
            res = await session.execute(select(GitRepoEntity).where(GitRepoEntity.full_name == full_name))
            ent = res.first()
            return _to_optional_repo(ent[0] if ent is not None else None)

    async def delete_github_repo(self, repo_id: str):
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                await session.execute(delete(GitRepoEntity).where(GitRepoEntity.id == repo_id))

    async def add_github_repo(self, repo: GitHubRepository) -> GitHubRepository:
        repo_id = repo.id
        if not repo_id or len(repo_id) == 0:
            repo_id = f"{uuid.uuid4()}"
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                existing = await session.execute(
                    select(GitRepoEntity).where(GitRepoEntity.full_name == repo.full_name)
                )
                ent = existing.first()
                if ent is not None:
                    return _to_repo(ent[0])
                r = GitRepoEntity(
                    id=repo_id,
                    full_name=repo.full_name,
                    json_data=pb_to_json(repo),
                )
                session.add(r)
                return _to_optional_repo(await session.get(GitRepoEntity, repo_id))

    async def update_repo_properties(self, repo_id: str, properties: GitProperties) -> GitHubRepository:
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                existing = await session.execute(
                    select(GitRepoEntity).where(GitRepoEntity.id == repo_id)
                )
                ent = existing.first()
                if ent is None:
                    raise ValueError(f"Repository with id {repo_id} not found")
                updated = _to_repo(ent[0])
                updated.properties.CopyFrom(properties)
                await session.execute(
                    update(GitRepoEntity)
                    .where(GitRepoEntity.id == repo_id)
                    .values(json_data=pb_to_json(updated))
                )
        return await self.get_github_repo(repo_id)

    async def get_web_sites(self) -> MutableSequence[WebSite]:
        async with AsyncSession(self._engine) as session:
            entities = await session.execute(select(WebsiteEntity))
            return [_to_web_site(e[0]) for e in entities.all()]

    async def get_web_site(self, site_id: str) -> Optional[WebSite]:
        async with AsyncSession(self._engine) as session:
            ent = await session.scalar(select(WebsiteEntity).where(WebsiteEntity.id == site_id))
            return _to_optional_web_site(ent)

    async def delete_web_site(self, site_id: str):
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                await session.execute(delete(WebsiteEntity).where(WebsiteEntity.id == site_id))

    async def add_web_site(self, site: WebSite) -> AddWebSiteData:
        site_id = site.id
        if not site_id or len(site_id) == 0:
            site_id = f"{uuid.uuid4()}"
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                existing = await session.scalar(
                    select(WebsiteEntity).where(WebsiteEntity.url == site.url)
                )
                if existing is not None:
                    return AddWebSiteData(_to_web_site(existing), created=False)
                s = WebsiteEntity(
                    id=site_id,
                    url=site.url,
                    json_data=pb_to_json(site),
                )
                session.add(s)
                return AddWebSiteData(
                    _to_optional_web_site(await session.get(WebsiteEntity, site_id)),
                    created=True,
                )

    async def next_processing_item(self) -> Optional[ProcessingItem]:
        next_processing_time = self._clock.now()
        async with AsyncSession(self._engine) as session:
            res = await session.execute(
                select(ProcessingItemEntity)
                .where(
                    ProcessingItemEntity.next_processing != None,
                    ProcessingItemEntity.next_processing < next_processing_time,
                )
                .order_by(ProcessingItemEntity.next_processing)
            )
            item = res.first()
            return _to_optional_item(item[0] if item is not None else None)

    async def set_next_processing_time(
            self, key: ProcessingItemKey,
            next_time: Optional[datetime.datetime],
            error: Optional[str] = None,
            processing_started_at: Optional[datetime.datetime] = None,
    ):
        key_str = json_format.MessageToJson(key, indent=None, sort_keys=True)
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                existing = await session.get(ProcessingItemEntity, key_str)
                if existing is not None:
                    await session.execute(
                        update(ProcessingItemEntity)
                        .where(ProcessingItemEntity.key == key_str)
                        .values(
                            next_processing=next_time,
                            last_error=error,
                            processing_started_at=processing_started_at,
                        )
                    )
                else:
                    session.add(ProcessingItemEntity(
                        key=key_str, next_processing=next_time, last_error=error, json_data="{}",
                    ))

    async def create_processing_time(
            self,
            key: ProcessingItemKey,
            request: Optional[ProcessingRequest] = None,
            schedule: Optional[Schedule] = None,
            next_time: Optional[datetime.datetime] = None,
    ):
        key_str = json_format.MessageToJson(key, indent=None, sort_keys=True)
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                session.add(ProcessingItemEntity(
                    key=key_str,
                    next_processing=next_time,
                    request_type=request.WhichOneof("type") if request else None,
                    reference_id=request.reference_id if request else None,
                    namespace=request.namespace if request else None,
                    created_by=request.created_by if request else None,
                    json_data=pb_to_json(ProcessingItem(
                        key=key,
                        schedule=schedule,
                        request=request,
                    )),
                ))

    async def update_processing_item(
            self,
            key: ProcessingItemKey,
            updater: Callable[[ProcessingItem], None],
            next_time: Optional[datetime.datetime],
    ):
        key_str = json_format.MessageToJson(key, indent=None, sort_keys=True)
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                existing = await session.get(ProcessingItemEntity, key_str)
                item = _to_item(existing)
                updater(item)
                await session.execute(
                    update(ProcessingItemEntity)
                    .where(ProcessingItemEntity.key == key_str)
                    .values(json_data=pb_to_json(item), next_processing=next_time)
                )

    async def delete_processing_item(self, key: ProcessingItemKey):
        key_str = json_format.MessageToJson(key, indent=None, sort_keys=True)
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                await session.execute(delete(ProcessingItemEntity).where(ProcessingItemEntity.key == key_str))

    async def add_processing_result(self, item: ProcessingItemResult) -> str:
        key_str = json_format.MessageToJson(item.key, indent=None, sort_keys=True)
        new_id = item.id
        if new_id is None or len(new_id) == 0:
            new_id = str(uuid.uuid4())
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                session.add(ProcessingItemResultEntity(
                    id=new_id,
                    key=key_str,
                    json_data=pb_to_json(item),
                    error_message=item.error_message,
                    namespace=item.request.namespace or None,
                    created_by=item.request.created_by or None,
                    reference_id=item.request.reference_id or None,
                    request_type=item.request.WhichOneof("type") if item.HasField("request") else None,
                ))
        return new_id

    async def get_processing_results(
            self,
            from_date: datetime.datetime,
            to_date: datetime.datetime,
            filter: ProcessingResultFilter,
    ) -> List[ProcessingItemResult]:
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                query = select(ProcessingItemResultEntity)
                if filter.namespace:
                    query = query.where(ProcessingItemResultEntity.namespace == filter.namespace)
                if filter.reference_id:
                    query = query.where(ProcessingItemResultEntity.reference_id == filter.reference_id)
                if filter.request_type:
                    query = query.where(ProcessingItemResultEntity.request_type == filter.request_type)
                result = await session.scalars(
                    query.order_by(ProcessingItemResultEntity.created_at.desc())
                )
                entities = result.all()
                return [_to_processing_item_result(entity) for entity in entities]

    async def set_processing_error(self, key: ProcessingItemKey, error: Optional[str] = None):
        key_str = json_format.MessageToJson(key, indent=None, sort_keys=True)
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                await session.execute(
                    update(ProcessingItemEntity)
                    .where(ProcessingItemEntity.key == key_str)
                    .values(last_error=error)
                )

    async def get_global_config(self) -> GlobalConfig:
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                all_configs = await session.execute(select(GlobalConfigEntity))
                ent = all_configs.first()
                if ent is None:
                    session.add(GlobalConfigEntity(id="global_config", json_data="{}"))
                    return GlobalConfig()
                return parse_json_pb(ent[0].json_data, GlobalConfig())

    async def set_global_config(self, config: GlobalConfig) -> GlobalConfig:
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                await session.execute(
                    update(GlobalConfigEntity)
                    .where(GlobalConfigEntity.id == "global_config")
                    .values(json_data=pb_to_json(config))
                )
        return await self.get_global_config()

    async def get_processing_time(self, key: ProcessingItemKey) -> Optional[ProcessingItem]:
        key_str = json_format.MessageToJson(key, indent=None, sort_keys=True)
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                existing = await session.get_one(ProcessingItemEntity, key_str)
                return _to_optional_item(existing)

    async def get_processing_result(self, result_id: str) -> Optional[ProcessingItemResult]:
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                existing = await session.get_one(ProcessingItemResultEntity, result_id)
                return _to_processing_item_result(existing) if existing is not None else None

    async def get_processing_items(self, filter: ProcessingItemsFilter) -> Sequence[ProcessingItem]:
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                query = select(ProcessingItemEntity)
                if filter.namespace:
                    query = query.where(ProcessingItemEntity.namespace == filter.namespace)
                if filter.reference_id:
                    query = query.where(ProcessingItemEntity.reference_id == filter.reference_id)
                if filter.request_type:
                    query = query.where(ProcessingItemEntity.request_type == filter.request_type)
                items = await session.scalars(query)
                return [_to_item(i) for i in items.all()]


def _to_optional_repo(ent: Optional[GitRepoEntity]) -> Optional[GitHubRepository]:
    return None if ent is None else _to_repo(ent)


def _to_repo(ent: GitRepoEntity) -> GitHubRepository:
    data = parse_json_pb(ent.json_data, GitHubRepository())
    data.id = ent.id
    return data


def _to_optional_web_site(ent: Optional[WebsiteEntity]) -> Optional[WebSite]:
    return None if ent is None else _to_web_site(ent)


def _to_web_site(ent: WebsiteEntity) -> WebSite:
    data = parse_json_pb(ent.json_data, WebSite())
    data.id = ent.id
    data.url = ent.url
    return data


def _to_optional_item(ent: Optional[ProcessingItemEntity]) -> Optional[ProcessingItem]:
    return None if ent is None else _to_item(ent)


def _to_item(ent: ProcessingItemEntity) -> ProcessingItem:
    data = parse_json_pb(ent.json_data, ProcessingItem())

    if ent.next_processing is None:
        data.ClearField("next_processing")
    else:
        data.next_processing = ent.next_processing

    if ent.last_processed is None:
        data.ClearField("last_processed")
    else:
        data.last_processed = ent.last_processed
    if ent.processing_started_at is None:
        data.ClearField("processing_started_at")
    else:
        data.processing_started_at = ent.processing_started_at
    data.last_error = ent.last_error if ent.last_error else ""
    data.no_processing = ent.no_processing
    data.key.CopyFrom(parse_json_pb(ent.key, ProcessingItemKey()))
    return data


def _to_processing_item_result(ent: ProcessingItemResultEntity) -> ProcessingItemResult:
    data = parse_json_pb(ent.json_data, ProcessingItemResult())
    data.id = ent.id
    data.key.CopyFrom(parse_json_pb(ent.key, ProcessingItemKey()))
    data.created_at.FromDatetime(ent.created_at)
    if ent.error_message:
        data.error_message = ent.error_message
    return data
