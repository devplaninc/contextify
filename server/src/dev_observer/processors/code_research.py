import asyncio
import dataclasses
import logging
import os
import shutil
from typing import Optional, List

from langgraph.graph.state import CompiledStateGraph
from langgraph.utils.config import ensure_config

from dev_observer.analysis.code.nodes import AnalysisState
from dev_observer.api.types.observations_pb2 import ObservationKey, Observation
from dev_observer.api.types.processing_pb2 import ProcessingItemResultData
from dev_observer.api.types.repo_pb2 import CodeResearchMeta, GitProvider, CodeResearchAreaMeta, \
    CodeResearchOrganizationMeta
from dev_observer.observations.provider import ObservationsProvider
from dev_observer.processors.observations import get_repo_key_pref, get_repo_owner_key_pref
from dev_observer.repository.cloner import clone_repository
from dev_observer.repository.provider import GitRepositoryProvider
from dev_observer.repository.types import ObservedRepo
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import Clock, RealClock, pb_to_json, parse_json_pb

REPO_RESEARCH_KIND = "repo_research"

_log = logging.getLogger(__name__)


@dataclasses.dataclass
class CodeResearchTask:
    general_prompt_prefix: str
    task_prompt_prefix: str
    repo_path: str
    repo_url: str
    repo_name: str
    repo_full_name: str
    max_iterations: int
    dir_key: ObservationKey
    area_title: str


class CodeResearchProcessor:
    _graph: CompiledStateGraph[AnalysisState, AnalysisState, AnalysisState]
    _git: GitRepositoryProvider
    _store: StorageProvider
    _observations: ObservationsProvider

    _clock: Clock

    def __init__(self,
                 graph: CompiledStateGraph[AnalysisState],
                 git: GitRepositoryProvider,
                 store: StorageProvider,
                 observations: ObservationsProvider,
                 clock: Clock = RealClock(),
                 ):
        self._graph = graph
        self._git = git
        self._store = store
        self._observations = observations
        self._clock = clock

    async def research_repository(self, repo: ObservedRepo) -> Optional[ProcessingItemResultData]:
        config = await self._store.get_global_config()
        analyzers = config.repo_analysis.research.analyzers
        if len(analyzers) == 0:
            return None

        general_prefix = config.repo_analysis.research.general_prefix
        if not general_prefix or len(general_prefix) == 0:
            return None

        conf = config.repo_analysis.research
        clone_result = await clone_repository(
            repo, self._git,
            max_size_mb=conf.max_repo_size_mb or 1000,
            depth="1",
        )
        repo_path = clone_result.path

        async def clean_up():
            if os.path.exists(repo_path):
                # noinspection PyTypeChecker
                await asyncio.to_thread(shutil.rmtree, repo_path, False)

        try:
            tasks: List[CodeResearchTask] = []
            for analyzer in analyzers:
                key = f"{get_repo_key_pref(repo.git_repo)}/{analyzer.file_name}"
                tasks.append(CodeResearchTask(
                    general_prompt_prefix=general_prefix,
                    task_prompt_prefix=analyzer.prompt_prefix,
                    repo_path=repo_path,
                    max_iterations=conf.max_iterations or 1,
                    dir_key=ObservationKey(kind=REPO_RESEARCH_KIND, name=analyzer.file_name, key=key),
                    repo_url=repo.url,
                    repo_name=repo.git_repo.name,
                    repo_full_name=repo.git_repo.full_name,
                    area_title=analyzer.name,
                ))

            coro_tasks = [self._process_task(t) for t in tasks]
            await asyncio.gather(*coro_tasks, return_exceptions=True)

            # Update aggregated summaries for the owner after completing all research tasks
            owner = repo.git_repo.full_name.split('/')[0]
            await self._update_aggregated_summaries(repo.git_repo.provider, owner)

            return ProcessingItemResultData(
                observations=[t.dir_key for t in tasks]
            )
        finally:
            await clean_up()

    async def _process_task(self, task: CodeResearchTask):
        in_state: AnalysisState = AnalysisState(
            repo_path=task.repo_path,
            max_iterations=task.max_iterations,
            general_prompt_prefix=task.general_prompt_prefix,
            task_prompt_prefix=task.task_prompt_prefix,
            repo_url=task.repo_url,
            repo_name=task.repo_name,
        )
        # noinspection PyTypeChecker
        response = await self._graph.ainvoke(
            in_state,
            ensure_config({"recursion_limit": 200}),
            output_keys=["full_analysis", "analysis_summary", "research_log"])

        dir_key = task.dir_key
        meta = CodeResearchMeta(
            summary=response.get("analysis_summary", ""),
            created_at=self._clock.now(),
            repo_full_name=task.repo_full_name,
            repo_url=task.repo_url,
            area_title=task.area_title,
            dir_key=task.dir_key,
        )
        meta_obs = Observation(
            key=ObservationKey(kind=dir_key.kind, name="meta.json", key=f"{dir_key.key}/meta.json"),
            content=pb_to_json(meta),
        )
        research_obs = Observation(
            key=ObservationKey(kind=dir_key.kind, name="research.md", key=f"{dir_key.key}/research.md"),
            content=response.get("full_analysis"),
        )
        # log_obs = Observation(
        #     key=ObservationKey(kind=dir_key.kind, name="research_log.json", key=f"{dir_key.key}/research_log.json"),
        #     content=json.dumps(response["research_log"], indent=2),
        # )
        await self._observations.store(research_obs)
        await self._observations.store(meta_obs)
        # await self._observations.store(log_obs)

    async def _update_aggregated_summaries(self, provider: GitProvider, repo_owner: str):
        # Get the owner prefix for filtering observations
        owner_prefix = get_repo_owner_key_pref(provider, repo_owner)

        observation_keys = await self._observations.list(REPO_RESEARCH_KIND, owner_prefix)

        # Filter for meta.json files only
        meta_keys = [key for key in observation_keys if key.name == "meta.json"]

        # Collect all area metas
        area_metas = []
        for meta_key in meta_keys:
            try:
                research_key = _find_corresponding_key(observation_keys, meta_key, "research.md")
                if not research_key:
                    continue
                observation = await self._observations.get(meta_key)
                meta = parse_json_pb(observation.content, CodeResearchMeta())
                area_meta = CodeResearchAreaMeta(research_key=research_key, meta=meta)
                area_metas.append(area_meta)
            except Exception as e:
                _log.warning(f"Failed to process meta observation {meta_key.key}: {e}")
                continue

        org_meta = CodeResearchOrganizationMeta(area_metas=area_metas)

        # Store the aggregated summary as summaries.json at the owner level
        summary_key = ObservationKey(
            kind=REPO_RESEARCH_KIND,
            name="org_meta.json",
            key=f"{owner_prefix}org_meta.json"
        )

        summary_obs = Observation(
            key=summary_key,
            content=pb_to_json(org_meta, indent=2)
        )

        await self._observations.store(summary_obs)
        _log.info(
            f"Updated aggregated summaries for {repo_owner} with {len(area_metas)} research areas")


def _find_corresponding_key(
        observation_keys: List[ObservationKey], key: ObservationKey, name: str,
) -> Optional[ObservationKey]:
    key_base = '/'.join(key.key.split('/')[:-1])  # Get path without last part
    expected_key = f"{key_base}/{name}"
    for obs_key in observation_keys:
        if obs_key.key == expected_key:
            return obs_key
    return None
