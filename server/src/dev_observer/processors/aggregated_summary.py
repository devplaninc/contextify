import asyncio
import dataclasses
import datetime
import logging
import os
import shutil
import tempfile
from typing import List, Sequence

from dev_observer.analysis.provider import AnalysisProvider
from dev_observer.api.types.config_pb2 import GlobalConfig
from dev_observer.api.types.observations_pb2 import ObservationKey, Observation
from dev_observer.api.types.processing_pb2 import AggregatedSummaryParams, ProcessingItemResultData, \
    PeriodicAggregationResult, RepoObservation
from dev_observer.common.schedule import pb_to_datetime
from dev_observer.flatten.flatten import FlattenResult, tokenize_file
from dev_observer.log import s_
from dev_observer.observations.provider import ObservationsProvider
from dev_observer.processors.flattening import FlatteningProcessor
from dev_observer.processors.git.changes import GitChangesHandler, ProcessGitChangesParams
from dev_observer.prompts.provider import PromptsProvider
from dev_observer.repository.provider import GitRepositoryProvider
from dev_observer.storage.provider import StorageProvider
from dev_observer.tokenizer.provider import TokenizerProvider


@dataclasses.dataclass
class AggregatedItem:
    header: str
    keys: Sequence[ObservationKey]

_log = logging.getLogger(__name__)


class AggregatedSummaryProcessor(FlatteningProcessor[AggregatedSummaryParams]):
    repository: GitRepositoryProvider
    tokenizer: TokenizerProvider
    git_changes_handler: GitChangesHandler
    storage: StorageProvider

    def __init__(
            self,
            analysis: AnalysisProvider,
            repository: GitRepositoryProvider,
            prompts: PromptsProvider,
            observations: ObservationsProvider,
            tokenizer: TokenizerProvider,
            git_changes_handler: GitChangesHandler,
            storage: StorageProvider
    ):
        super().__init__(analysis, prompts, observations)
        self.repository = repository
        self.tokenizer = tokenizer
        self.git_changes_handler=git_changes_handler
        self.storage = storage

    async def get_flatten(self, params: AggregatedSummaryParams, config: GlobalConfig) -> FlattenResult:
        items: List[AggregatedItem] = []
        end_date = pb_to_datetime(params.end_date)
        result = PeriodicAggregationResult()
        for repo_id in params.target.git_repo_ids:
            repo = await self.storage.get_git_repo(repo_id)
            if repo is None:
                _log.warning(s_("Repo not found", repo_id=repo_id))
                continue
            git_result = await self.git_changes_handler.process_git_changes(ProcessGitChangesParams(
                repo_id=repo_id,
                end_date=end_date,
                look_back_days=params.look_back_days,
            ))
            repo = git_result.repo
            header = f"Changes for repository **{repo.full_name}**"
            result.repo_observations.append(RepoObservation(
                repo_id=repo_id,
                observations=git_result.observation_keys,
            ))
            items.append(AggregatedItem(header=header, keys=git_result.observation_keys))

        # Download all observations in parallel
        async def process_item(item: AggregatedItem):
            obs: List[Observation] = []
            for key in item.keys:
                obs.append(await self.observations.get(key))
            content = "\n\n".join([o.content for o in obs])
            return f"# {item.header}\n\n{content}"

        parts = await asyncio.gather(*[process_item(item) for item in items])

        temp_dir = tempfile.mkdtemp(prefix="aggregated_summary_")
        combined_file_path = os.path.join(temp_dir, "combined_observations.md")

        with open(combined_file_path, 'w', encoding='utf-8') as f:
            start_date = end_date - datetime.timedelta(params.look_back_days)
            f.write(f"# Summaries of changes between: {_fmt_date(start_date)} - {_fmt_date(end_date)}:\n\n")
            for part in parts:
                f.write(part)
                f.write("\n\n---\n\n")

        # Tokenize the combined file
        tokenize_result = tokenize_file(combined_file_path, temp_dir, self.tokenizer, config)

        # Create cleanup function
        def clean_up():
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                return True
            return False

        return FlattenResult(
            full_file_path=combined_file_path,
            file_paths=tokenize_result.file_paths,
            total_tokens=tokenize_result.total_tokens,
            clean_up=clean_up,
            result_data=ProcessingItemResultData(
                periodic_aggregation=result,
            )
        )


def _fmt_date(d: datetime.datetime) -> str:
    return d.strftime("%Y-%m-%d %H:%M:%S")
