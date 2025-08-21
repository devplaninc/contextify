import asyncio
import logging
from datetime import date
from typing import Sequence

from dev_observer.analysis.provider import AnalysisProvider
from dev_observer.api.types.observations_pb2 import Analyzer, ObservationKey, Observation
from dev_observer.api.types.repo_pb2 import GitRepository
from dev_observer.log import s_
from dev_observer.observations.provider import ObservationsProvider
from dev_observer.processors.observations import get_repo_key_pref
from dev_observer.prompts.provider import PromptsProvider
from dev_observer.storage.provider import StorageProvider

_log = logging.getLogger(__name__)


async def backfill_analysis_summaries(
        force: bool,
        storage: StorageProvider,
        observations: ObservationsProvider,
        prompts: PromptsProvider,
        analysis: AnalysisProvider,
):
    ext = {"op": "backfill_analysis_summaries"}
    _log.info(s_("Starting backfilling analysis summaries", **ext))

    config = await storage.get_global_config()
    if len(config.analysis.repo_analyzers) == 0 or config.repo_analysis.disabled:
        _log.info(s_("No repo analyzers configured", **ext))
        return

    repos = await storage.get_git_repos()
    if not repos:
        _log.info(s_("No repositories found", **ext))
        return

    _log.info(s_("Processing", repos_count=len(repos), **ext))
    tasks = [_process_repo_summaries(force, r, config.analysis.repo_analyzers, observations, prompts, analysis) for r in repos]
    await asyncio.gather(*tasks)

    _log.info(s_("Completed", **ext))


async def _process_repo_summaries(
        force: bool,
        repo: GitRepository,
        analyzers: Sequence[Analyzer],
        observations: ObservationsProvider,
        prompts: PromptsProvider,
        analysis: AnalysisProvider,
):
    repo_id = repo.id if hasattr(repo, 'id') else repo.full_name
    _log.debug(s_("Processing repo summaries", repo_id=repo_id))

    repo_key_prefix = get_repo_key_pref(repo)

    # Process each analyzer
    for analyzer in analyzers:
        # Analysis file key and summary file key
        analysis_file = analyzer.file_name
        summary_file = f"__summary__{analysis_file}"

        analysis_key = f"{repo_key_prefix}/{analysis_file}"
        summary_key = f"{repo_key_prefix}/{summary_file}"

        analysis_obs_key = ObservationKey(kind="repos", name=analysis_file, key=analysis_key)
        if not await observations.exists(analysis_obs_key):
            _log.debug(s_("Analysis file not found, skipping", repo_id=repo_id, analysis_file=analysis_file))
            continue

        summary_obs_key = ObservationKey(kind="repos", name=summary_file, key=summary_key)
        if not force:
            if await observations.exists(summary_obs_key):
                _log.debug(s_("Summary already exists, skipping", repo_id=repo_id, summary_file=summary_file))
                continue

        generated = await _generate_summary(analysis_obs_key, summary_obs_key, analyzer, observations, prompts,
                                            analysis)
        _log.info(s_("Summary processed", repo_id=repo_id, summary_file=summary_file, generated=generated))


async def _generate_summary(
        analysis_key: ObservationKey,
        summary_key: ObservationKey,
        analyzer: Analyzer,
        observations: ObservationsProvider,
        prompts: PromptsProvider,
        analysis: AnalysisProvider,
) -> bool:
    analysis_obs = await observations.get(analysis_key)
    content = analysis_obs.content

    prompt_name = f"{analyzer.prompt_prefix}_summarize_analysis"
    prompt = await prompts.get_optional(prompt_name, {"content": content})

    if prompt is None:
        return False

    session_id = f"{date.today().strftime('%Y-%m-%d')}.{analysis_key.key}"
    result = await analysis.analyze(prompt, session_id)

    summary_obs = Observation(key=summary_key, content=result.analysis)
    await observations.store(summary_obs)
    return True
