import dataclasses
from datetime import datetime

from dev_observer.api.types.repo_pb2 import GitRepository


@dataclasses.dataclass
class ObservedRepo:
    url: str
    git_repo: GitRepository


@dataclasses.dataclass
class ObservedGitChanges:
    repo: ObservedRepo
    from_date: datetime
    to_date: datetime


@dataclasses.dataclass
class ObservedAggregatedChanges:
    repo: ObservedRepo
    from_date: datetime
    to_date: datetime
