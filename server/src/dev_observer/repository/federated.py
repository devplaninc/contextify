from typing import Optional, Dict

from dev_observer.api.types.repo_pb2 import GitProvider
from dev_observer.repository.provider import GitRepositoryProvider, RepositoryInfo
from dev_observer.repository.types import ObservedRepo


class FederatedGitProvider(GitRepositoryProvider):
    _providers: Dict[GitProvider, GitRepositoryProvider]

    def __init__(self, providers: Dict[GitProvider, GitRepositoryProvider]):
        self._providers = providers

    async def get_repo(self, repo: ObservedRepo) -> RepositoryInfo:
        return await self._get(repo.git_repo.provider).get_repo(repo)

    async def clone(self, repo: ObservedRepo, info: RepositoryInfo, dest: str, depth: Optional[str] = None):
        await self._get(repo.git_repo.provider).clone(repo, info, dest, depth)

    def _get(self, provider_type: GitProvider) -> GitRepositoryProvider:
        if provider_type not in self._providers:
            raise ValueError(f"No repository provider registered for provider type: {provider_type}")

        return self._providers[provider_type]