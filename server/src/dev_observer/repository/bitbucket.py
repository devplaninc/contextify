import logging
import subprocess
from abc import abstractmethod
from typing import Protocol, Optional

import requests

from dev_observer.api.types.repo_pb2 import GitProperties, GitMeta
from dev_observer.repository.provider import GitRepositoryProvider, RepositoryInfo
from dev_observer.repository.types import ObservedRepo
from dev_observer.repository.util import get_valid_repo_meta
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import Clock, RealClock

_log = logging.getLogger(__name__)


class BitBucketAuthProvider(Protocol):
    @abstractmethod
    async def get_auth_headers(self, repo: ObservedRepo) -> dict:
        """Get authentication headers for BitBucket API requests."""
        ...

    @abstractmethod
    async def get_cli_token_prefix(self, repo: ObservedRepo) -> str:
        """Get token prefix for git CLI operations."""
        ...


class BitBucketProvider(GitRepositoryProvider):
    _auth_provider: BitBucketAuthProvider
    _storage: StorageProvider
    _clock: Clock

    def __init__(self, auth_provider: BitBucketAuthProvider, storage: StorageProvider, clock: Clock = RealClock()):
        self._auth_provider = auth_provider
        self._storage = storage
        self._clock = clock

    async def get_repo(self, repo: ObservedRepo) -> RepositoryInfo:
        full_name = repo.git_repo.full_name
        parts = full_name.split("/")
        owner = parts[0]

        meta, expired = get_valid_repo_meta(repo.git_repo)
        if meta is None or expired:
            # Fetch repository metadata from BitBucket API
            auth_headers = await self._auth_provider.get_auth_headers(repo)

            # BitBucket API v2.0 endpoint for repository information
            api_url = f"https://api.bitbucket.org/2.0/repositories/{full_name}"

            try:
                response = requests.get(api_url, headers=auth_headers)
                response.raise_for_status()
                repo_data = response.json()

                # Extract repository information
                size_kb = repo_data.get('size', 0) // 1024  # Convert bytes to KB
                clone_url = f"https://bitbucket.org/{full_name}.git"

                meta = GitMeta(
                    last_refresh=self._clock.now(),
                    size_kb=size_kb,
                    clone_url=clone_url,
                )

                # Update stored repository with metadata
                stored_repo = repo.git_repo
                if not stored_repo.HasField("properties"):
                    stored_repo.properties.CopyFrom(GitProperties())
                stored_repo.properties.meta.CopyFrom(meta)
                repo.git_repo = await self._storage.update_repo_properties(stored_repo.id, stored_repo.properties)

            except requests.RequestException as e:
                _log.error(f"Failed to fetch BitBucket repository metadata for {full_name}: {e}")
                # Fallback to basic information
                meta = GitMeta(
                    last_refresh=self._clock.now(),
                    size_kb=0,
                    clone_url=f"https://bitbucket.org/{full_name}.git",
                )

        return RepositoryInfo(
            owner=owner,
            name=repo.git_repo.name,
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

    async def get_authenticated_url(self, repo: ObservedRepo) -> str:
        info = await self.get_repo(repo)
        token = await self._auth_provider.get_cli_token_prefix(repo)
        return info.clone_url.replace("https://", f"https://{token}@")
