import datetime
import logging
import uuid
from typing import Optional, MutableSequence, List, Sequence, Callable, cast

from google.protobuf import json_format
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession

from dev_observer.api.types.config_pb2 import GlobalConfig
from dev_observer.api.types.processing_pb2 import ProcessingItem, ProcessingItemKey, \
    ProcessingItemResult, ProcessingResultFilter, ProcessingItemsFilter, ProcessingItemData
from dev_observer.api.types.repo_pb2 import GitRepository, GitProperties, RepoToken, GitProvider
from dev_observer.api.types.sites_pb2 import WebSite
from dev_observer.common.crypto import Encryptor
from dev_observer.storage.postgresql.model import GitRepoEntity, ProcessingItemEntity, GlobalConfigEntity, \
    WebsiteEntity, ProcessingItemResultEntity, RepoTokenEntity
from dev_observer.storage.provider import StorageProvider, AddWebSiteData
from dev_observer.util import parse_json_pb, pb_to_json, Clock, RealClock

_log = logging.getLogger(__name__)


class PostgresqlStorageProvider(StorageProvider):
    _engine: AsyncEngine
    _encryptor: Encryptor
    _clock: Clock

    def __init__(self, url: str, encryptor: Encryptor, echo: bool = False, clock: Clock = RealClock()):
        self._engine = create_async_engine(url, echo=echo)
        self._encryptor = encryptor
        self._clock = clock

    async def get_git_repos(self) -> MutableSequence[GitRepository]:
        async with AsyncSession(self._engine) as session:
            entities = await session.execute(select(GitRepoEntity))
            return [_to_repo(e[0]) for e in entities.all()]

    async def get_git_repo(self, repo_id: str) -> Optional[GitRepository]:
        async with AsyncSession(self._engine) as session:
            return _to_optional_repo(await session.get(GitRepoEntity, repo_id))

    async def delete_git_repo(self, repo_id: str):
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                await session.execute(delete(GitRepoEntity).where(GitRepoEntity.id == repo_id))

    async def add_git_repo(self, repo: GitRepository) -> GitRepository:
        repo_id = repo.id
        if not repo_id or len(repo_id) == 0:
            repo_id = f"{uuid.uuid4()}"
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                existing = await session.execute(
                    select(GitRepoEntity)
                    .where(GitRepoEntity.full_name == repo.full_name and GitRepoEntity.provider == repo.provider)
                )
                ent = existing.first()
                if ent is not None:
                    return _to_repo(ent[0])
                r = GitRepoEntity(
                    id=repo_id,
                    full_name=repo.full_name,
                    json_data=pb_to_json(repo),
                    provider=repo.provider,
                )
                session.add(r)
                return _to_optional_repo(await session.get(GitRepoEntity, repo_id))

    async def update_repo_properties(self, repo_id: str, properties: GitProperties) -> GitRepository:
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
        return await self.get_git_repo(repo_id)

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
        key_str = _to_key_str(key)
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
            data: Optional[ProcessingItemData] = None,
            next_time: Optional[datetime.datetime] = None,
    ):
        key_str = _to_key_str(key)
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                is_req = data and data.WhichOneof("type") == "request"
                session.add(ProcessingItemEntity(
                    key=key_str,
                    next_processing=next_time,
                    request_type=data.request.WhichOneof("type") if is_req else None,
                    reference_id=data.reference_id if data else None,
                    namespace=data.namespace if data else None,
                    created_by=data.created_by if data else None,
                    json_data=pb_to_json(ProcessingItem(key=key, data=data)),
                ))

    async def update_processing_item(
            self,
            key: ProcessingItemKey,
            updater: Callable[[ProcessingItem], ProcessingItem],
            next_time: Optional[datetime.datetime] = None,
    ):
        key_str = _to_key_str(key)
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                existing = await session.get(ProcessingItemEntity, key_str)
                item = _to_item(existing)
                updated = updater(item)
                values: dict = {"json_data": pb_to_json(updated)}
                if next_time is not None:
                    values["next_processing"] = next_time
                await session.execute(
                    update(ProcessingItemEntity)
                    .where(ProcessingItemEntity.key == key_str)
                    .values(**values)
                )

    async def delete_processing_item(self, key: ProcessingItemKey):
        key_str = _to_key_str(key)
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                await session.execute(delete(ProcessingItemEntity).where(ProcessingItemEntity.key == key_str))

    async def add_processing_result(self, item: ProcessingItemResult) -> str:
        key_str = _to_key_str(item.key)
        new_id = item.id
        if new_id is None or len(new_id) == 0:
            new_id = str(uuid.uuid4())
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                is_req = item.HasField("data") and item.data.WhichOneof("type") == "request"
                session.add(ProcessingItemResultEntity(
                    id=new_id,
                    key=key_str,
                    json_data=pb_to_json(item),
                    error_message=item.error_message,
                    namespace=item.data.namespace or None,
                    created_by=item.data.created_by or None,
                    reference_id=item.data.reference_id or None,
                    request_type=item.data.request.WhichOneof("type") if is_req else None,
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
                query = select(ProcessingItemResultEntity).where(
                    ProcessingItemResultEntity.created_at.between(from_date, to_date)
                )
                if filter.namespace:
                    query = query.where(ProcessingItemResultEntity.namespace == filter.namespace)
                if filter.reference_id:
                    query = query.where(ProcessingItemResultEntity.reference_id == filter.reference_id)
                if filter.request_type:
                    query = query.where(ProcessingItemResultEntity.request_type == filter.request_type)
                if len(filter.keys) > 0:
                    query = query.where(ProcessingItemResultEntity.key.in_([_to_key_str(k) for k in filter.keys]))
                result = await session.scalars(
                    query.order_by(ProcessingItemResultEntity.created_at.desc())
                )
                entities = result.all()
                return [_to_processing_item_result(entity) for entity in entities]

    async def set_processing_error(self, key: ProcessingItemKey, error: Optional[str] = None):
        key_str = _to_key_str(key)
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

    async def get_processing_item(self, key: ProcessingItemKey) -> Optional[ProcessingItem]:
        key_str = _to_key_str(key)
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
                if len(filter.keys) > 0:
                    query = query.where(ProcessingItemEntity.key.in_([_to_key_str(k) for k in filter.keys]))
                items = await session.scalars(query)
                return [_to_item(i) for i in items.all()]

    # Token CRUD operations
    async def add_token(self, token: RepoToken) -> RepoToken:
        token_id = token.id
        if not token_id or len(token_id) == 0:
            token_id = f"{uuid.uuid4()}"
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                t = RepoTokenEntity(
                    id=token_id,
                    namespace=token.namespace,
                    provider=token.provider,
                    workspace=token.workspace if token.HasField("workspace") else None,
                    repo=token.repo if token.HasField("repo") else None,
                    system=token.system,
                    token=self._encryptor.encrypt(token.token, token_id),
                    expires_at=token.expires_at.ToDatetime() if token.HasField("expires_at") else None,
                )
                session.add(t)
                return self._to_token(await session.get(RepoTokenEntity, token_id))

    async def get_token(self, token_id: str) -> Optional[RepoToken]:
        async with AsyncSession(self._engine) as session:
            ent = await session.get(RepoTokenEntity, token_id)
            return self._to_optional_token(ent)

    async def update_token(self, token_id: str, token: str) -> Optional[RepoToken]:
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                await session.execute(
                    update(RepoTokenEntity)
                    .where(RepoTokenEntity.id == token_id)
                    .values(
                        token=self._encryptor.encrypt(token, token_id),
                    )
                )
        return await self.get_token(token_id)

    async def delete_token(self, token_id: str):
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                await session.execute(delete(RepoTokenEntity).where(RepoTokenEntity.id == token_id))

    async def list_tokens(self, namespace: Optional[str] = None) -> List[RepoToken]:
        async with AsyncSession(self._engine) as session:
            query = select(RepoTokenEntity)
            if namespace:
                query = query.where(RepoTokenEntity.namespace == namespace)
            entities = await session.scalars(query)
            return [self._to_token(ent) for ent in entities.all()]

    async def find_tokens(self, provider: int, workspace: Optional[str] = None, repo: Optional[str] = None) -> List[
        RepoToken]:
        """Find tokens by provider, workspace, and repo. Returns tokens in priority order: workspace, system, repo."""
        async with AsyncSession(self._engine) as session:
            query = select(RepoTokenEntity).where(RepoTokenEntity.provider == provider)

            # Build conditions for different token types
            conditions = []

            # Workspace token condition
            if workspace:
                conditions.append(
                    (RepoTokenEntity.workspace == workspace) &
                    (RepoTokenEntity.repo.is_(None)) &
                    (RepoTokenEntity.system == False)
                )

            # System token condition
            conditions.append(RepoTokenEntity.system == True)

            # Repo token condition
            if repo:
                conditions.append(
                    (RepoTokenEntity.repo == repo) &
                    (RepoTokenEntity.system == False)
                )

            if conditions:
                from sqlalchemy import or_
                query = query.where(or_(*conditions))

            entities = await session.scalars(query)
            return [self._to_token(ent) for ent in entities.all()]

    def _to_optional_token(self, ent: Optional[RepoTokenEntity]) -> Optional[RepoToken]:
        return None if ent is None else self._to_token(ent)

    def _to_token(self, ent: RepoTokenEntity) -> RepoToken:
        token = RepoToken(
            id=ent.id,
            namespace=ent.namespace,
            provider=cast(GitProvider, ent.provider),
            system=ent.system,
            token=self._encryptor.decrypt(ent.token, ent.id),
        )

        # Set optional fields
        if ent.workspace:
            token.workspace = ent.workspace
        if ent.repo:
            token.repo = ent.repo
        if ent.expires_at:
            token.expires_at.FromDatetime(ent.expires_at)

        # Set timestamps
        token.created_at.FromDatetime(ent.created_at)
        token.updated_at.FromDatetime(ent.updated_at)

        return token


def _to_optional_repo(ent: Optional[GitRepoEntity]) -> Optional[GitRepository]:
    return None if ent is None else _to_repo(ent)


def _to_repo(ent: GitRepoEntity) -> GitRepository:
    data = parse_json_pb(ent.json_data, GitRepository())
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


def _to_key_str(key: ProcessingItemKey) -> str:
    return json_format.MessageToJson(key, indent=None, sort_keys=True)
