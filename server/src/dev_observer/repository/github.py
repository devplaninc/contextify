import logging
import subprocess
from abc import abstractmethod
from datetime import datetime
from typing import Protocol, Optional

from github import Auth
from github import Github

from dev_observer.api.types.repo_pb2 import GitProperties, GitMeta
from dev_observer.repository.provider import GitRepositoryProvider, RepositoryInfo
from dev_observer.repository.types import ObservedRepo
from dev_observer.repository.util import get_valid_repo_meta
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import Clock, RealClock

_log = logging.getLogger(__name__)


class GithubAuthProvider(Protocol):
    @abstractmethod
    async def get_auth(self, repo: ObservedRepo) -> Auth:
        ...

    @abstractmethod
    async def get_cli_token_prefix(self, repo: ObservedRepo) -> str:
        ...


class GithubProvider(GitRepositoryProvider):
    _auth_provider: GithubAuthProvider
    _storage: StorageProvider
    _clock: Clock

    def __init__(self, auth_provider: GithubAuthProvider, storage: StorageProvider, clock: Clock = RealClock()):
        self._auth_provider = auth_provider
        self._storage = storage
        self._clock = clock

    async def get_repo(self, repo: ObservedRepo) -> RepositoryInfo:
        full_name = repo.github_repo.full_name
        parts = full_name.split("/")
        owner = parts[0]
        meta = get_valid_repo_meta(repo.github_repo)
        if meta is None:
            auth = await self._auth_provider.get_auth(repo)
            with Github(auth=auth) as gh:
                gh_repo = gh.get_repo(full_name)
            meta = GitMeta(
                last_refresh=self._clock.now(),
                size_kb=gh_repo.size,
                clone_url=gh_repo.clone_url,
            )
            stored_repo = repo.github_repo
            if not stored_repo.HasField("properties"):
                stored_repo.properties.CopyFrom(GitProperties())
            stored_repo.properties.meta.CopyFrom(meta)
            repo.github_repo = await self._storage.update_repo_properties(stored_repo.id, stored_repo.properties)

        return RepositoryInfo(
            owner=owner,
            name=repo.github_repo.name,
            clone_url=meta.clone_url,
            size_kb=meta.size_kb,
        )

    async def clone(self, repo: ObservedRepo, info: RepositoryInfo, dest: str, depth: Optional[str] = None):
        token = await self._auth_provider.get_cli_token_prefix(repo)
        clone_url = info.clone_url.replace("https://", f"https://{token}@")
        cmd = ["git", "clone"]
        if depth is not None:
            cmd.append(f"--depth={depth}")
        cmd.append(clone_url)
        cmd.append(dest)
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode != 0:
            raise RuntimeError(f"Failed to clone repository: {result.stderr}")
