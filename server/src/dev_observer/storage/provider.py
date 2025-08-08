import dataclasses
import datetime
from collections.abc import Callable
from typing import Protocol, Optional, MutableSequence, List, Sequence

from dev_observer.api.types.config_pb2 import GlobalConfig
from dev_observer.api.types.processing_pb2 import ProcessingItem, ProcessingItemKey, ProcessingItemResult, \
    ProcessingResultFilter, ProcessingItemsFilter, ProcessingItemData
from dev_observer.api.types.repo_pb2 import GitRepository, GitProperties, ReposFilter
from dev_observer.api.types.sites_pb2 import WebSite
from dev_observer.api.types.tokens_pb2 import AuthToken, AuthTokenProvider, TokensFilter


@dataclasses.dataclass
class AddWebSiteData:
    site: WebSite
    created: bool


class StorageProvider(Protocol):
    async def get_git_repos(self) -> MutableSequence[GitRepository]:
        ...

    async def filter_git_repos(self, filter: ReposFilter) -> MutableSequence[GitRepository]:
        ...

    async def get_git_repo(self, repo_id: str) -> Optional[GitRepository]:
        ...

    async def delete_git_repo(self, repo_id: str):
        ...

    async def add_git_repo(self, repo: GitRepository) -> GitRepository:
        ...

    async def update_repo_properties(self, id: str, properties: GitProperties) -> GitRepository:
        ...

    async def get_web_sites(self) -> MutableSequence[WebSite]:
        ...

    async def get_web_site(self, site_id: str) -> Optional[WebSite]:
        ...

    async def delete_web_site(self, site_id: str):
        ...

    async def add_web_site(self, site: WebSite) -> AddWebSiteData:
        ...

    async def next_processing_item(self) -> Optional[ProcessingItem]:
        ...

    async def create_processing_time(
            self,
            key: ProcessingItemKey,
            data: Optional[ProcessingItemData] = None,
            next_time: Optional[datetime.datetime] = None,
    ):
        ...

    async def get_processing_items(self, filter: ProcessingItemsFilter) -> Sequence[ProcessingItem]:
        ...

    async def update_processing_item(self,
                                     key: ProcessingItemKey,
                                     updater: Callable[[ProcessingItem], ProcessingItem],
                                     next_time: Optional[datetime.datetime] = None):
        ...

    async def delete_processing_item(self, key: ProcessingItemKey):
        ...

    async def set_next_processing_time(
            self, key: ProcessingItemKey, next_time: Optional[datetime.datetime], error: Optional[str] = None,
            processing_started_at: Optional[datetime.datetime] = None,
    ):
        ...

    async def get_processing_item(self, key: ProcessingItemKey) -> Optional[ProcessingItem]:
        ...

    async def set_processing_error(self, key: ProcessingItemKey, error: Optional[str] = None):
        ...

    async def get_global_config(self) -> GlobalConfig:
        ...

    async def set_global_config(self, config: GlobalConfig) -> GlobalConfig:
        ...

    async def add_processing_result(self, item: ProcessingItemResult):
        ...

    async def get_processing_results(
            self, from_date: datetime.datetime, to_date: datetime.datetime, filter: ProcessingResultFilter,
    ) -> List[ProcessingItemResult]:
        ...

    async def get_processing_result(self, result_id: str) -> Optional[ProcessingItemResult]:
        ...

    async def find_tokens(
            self, provider: AuthTokenProvider, workspace: Optional[str] = None, repo: Optional[str] = None,
    ) -> List[AuthToken]:
        ...

    async def list_tokens(self, filter: Optional[TokensFilter] = None) -> List[AuthToken]:
        ...

    async def delete_token(self, token_id: str):
        ...

    async def update_token(self, token_id: str, token: str) -> Optional[AuthToken]:
        ...

    async def get_token(self, token_id: str) -> Optional[AuthToken]:
        ...

    async def add_token(self, token: AuthToken, old_token_id: Optional[str] = None) -> AuthToken:
        ...
