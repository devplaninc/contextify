import dataclasses
from datetime import datetime

from dev_observer.api.types.repo_pb2 import GitHubRepository


@dataclasses.dataclass
class ObservedRepo:
    url: str
    github_repo: GitHubRepository


@dataclasses.dataclass
class ObservedGitChanges:
    repo: ObservedRepo
    from_date: datetime
    to_date: datetime
