import asyncio
import logging

from dev_observer.api.types.repo_pb2 import GitRepository, GitProperties, GitMeta, TokensInfo
from dev_observer.log import s_
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import RealClock, Clock

_log = logging.getLogger(__name__)


def persist_repo_tokens_info_async(store, repo: GitRepository, tokens_count: int, clock: Clock = RealClock()):
    async def _store():
        try:
            await persist_repo_tokens_info(store, repo, tokens_count, clock)
        except Exception as e:
            _log.error(s_("Failed to persist repo tokens info", repo=repo, err=e, exc_info=e))

    asyncio.create_task(_store())


async def persist_repo_tokens_info(
        store: StorageProvider, repo: GitRepository, tokens_count: int, clock: Clock = RealClock()):
    props = GitProperties()
    if repo.HasField("properties"):
        props.CopyFrom(repo.properties)
    meta = GitMeta()
    if props.HasField("meta"):
        meta.CopyFrom(props.meta)
    meta.tokens_info.CopyFrom(TokensInfo(created_at=clock.now(), tokens_count=tokens_count))
    props.meta.CopyFrom(meta)
    await store.update_repo_properties(repo.id, props)
