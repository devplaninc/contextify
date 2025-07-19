import dataclasses
from abc import abstractmethod
from typing import Protocol, Optional

from dev_observer.repository.types import ObservedRepo


@dataclasses.dataclass
class RepositoryInfo:
    owner: str
    name: str
    clone_url: str
    size_kb: int


class GitRepositoryProvider(Protocol):
    @abstractmethod
    async def get_repo(self, repo: ObservedRepo) -> RepositoryInfo:
        ...

    @abstractmethod
    async def clone(self, repo: ObservedRepo, info: RepositoryInfo, dest: str, depth: Optional[str] = None):
        ...
