import dataclasses
import datetime
import logging
from typing import Optional, List

from dev_observer.api.types.observations_pb2 import ObservationKey
from dev_observer.api.types.repo_pb2 import GitHubRepository
from dev_observer.common.errors import TerminalError
from dev_observer.log import s_
from dev_observer.observations.provider import ObservationsProvider
from dev_observer.processors.flattening import ObservationRequest
from dev_observer.processors.git_changes import GitChangesProcessor
from dev_observer.repository.types import ObservedRepo, ObservedGitChanges
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import Clock, RealClock

_log = logging.getLogger(__name__)


@dataclasses.dataclass
class ProcessGitChangesParams:
    end_date: datetime.datetime
    look_back_days: int
    repo_id: str


@dataclasses.dataclass
class GitChangesResult:
    repo: GitHubRepository
    observation_keys: List[ObservationKey]


class GitChangesHandler:
    _git_changes_processor: GitChangesProcessor
    _storage: StorageProvider
    _observations: ObservationsProvider
    _clock: Clock

    def __init__(self,
                 git_changes_processor: GitChangesProcessor,
                 storage: StorageProvider,
                 observations: ObservationsProvider,
                 clock: Clock = RealClock(),
                 ):
        self._git_changes_processor = git_changes_processor
        self._storage = storage
        self._observations = observations
        self._clock = clock

    async def process_git_changes(self, params: ProcessGitChangesParams) -> Optional[GitChangesResult]:
        config = await self._storage.get_global_config()
        if not config.analysis.HasField("default_git_changes_analyzer"):
            _log.warning(s_("Git change analysis disabled"))
            return None

        repo_id = params.repo_id
        extra = {"op": "process_git_changes", "repo_id": repo_id}
        repo = await self._storage.get_github_repo(repo_id)
        if repo is None:
            _log.error(s_("Github repo not found", **extra))
            raise TerminalError(f"Repo with id [{repo_id}] is not found")
        _log.debug(s_("Processing git changes repo", repo=repo))
        requests: List[ObservationRequest] = []
        end_date = params.end_date
        from_date = end_date - datetime.timedelta(params.look_back_days)
        analyzer = config.analysis.default_git_changes_analyzer
        period_str = f"{end_date.strftime('%Y%m%dT%H%M')}_{params.look_back_days}d"
        key = ObservationKey(
            kind="git_changes",
            name=analyzer.file_name,
            key=f"{repo.full_name}/{period_str}/{analyzer.file_name}",
        )
        if await self._observations.exists(key):
            return GitChangesResult(repo=repo, observation_keys=[key])
        requests.append(ObservationRequest(prompt_prefix=analyzer.prompt_prefix, key=key))
        observed_repo = ObservedRepo(url=repo.url, github_repo=repo)
        params = ObservedGitChanges(repo=observed_repo, from_date=from_date, to_date=end_date)
        keys = await self._git_changes_processor.process(params, requests, config)
        return GitChangesResult(repo=repo, observation_keys=keys)
