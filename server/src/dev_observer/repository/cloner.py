import dataclasses
import logging
import tempfile
from typing import Optional

from dev_observer.api.types.config_pb2 import GlobalConfig
from dev_observer.log import s_
from dev_observer.repository.types import ObservedRepo
from dev_observer.repository.provider import GitRepositoryProvider, RepositoryInfo

_log = logging.getLogger(__name__)


@dataclasses.dataclass
class CloneResult:
    """Result of cloning a repository."""
    path: str
    repo: RepositoryInfo


async def clone_repository(
        repo: ObservedRepo,
        provider: GitRepositoryProvider,
        max_size_mb: Optional[int] = None,
        depth: Optional[str] = None,
) -> CloneResult:
    max_size_kb = 100_000
    if max_size_mb is not None and max_size_mb > 0:
        max_size_kb = max_size_mb * 1024
    info = await provider.get_repo(repo)
    _log.debug(s_("Retrieved repository info", repo=repo, info=info, max_size_kb=max_size_kb))
    if info.size_kb > max_size_kb:
        raise ValueError(
            f"Repository size ({info.size_kb} KB) exceeds the maximum allowed size ({max_size_kb} KB)"
        )

    temp_dir = tempfile.mkdtemp(prefix=f"git_repo_{info.name}")
    extra = {"repo": repo, "info": info, "dest": temp_dir, "depth": depth}
    _log.debug(s_("Cloning...", **extra))
    await provider.clone(repo, info, temp_dir, depth)
    _log.debug(s_("Cloned.", **extra))
    return CloneResult(path=temp_dir, repo=info)
