import asyncio
import logging
from datetime import timedelta
from typing import List, Optional

from dev_observer.api.types.observations_pb2 import ObservationKey
from dev_observer.api.types.processing_pb2 import ProcessingItem, ProcessingRequest, ProcessGitChangesRequest, \
    ProcessingItemResult, ProcessingItemKey, PeriodicAggregation, ProcessingItemResultData
from dev_observer.common.errors import TerminalError
from dev_observer.common.schedule import get_next_date, pb_to_datetime
from dev_observer.log import s_
from dev_observer.processors.aggregated_summary import AggregatedSummaryProcessor
from dev_observer.processors.flattening import ObservationRequest
from dev_observer.processors.git.changes import GitChangesHandler, ProcessGitChangesParams
from dev_observer.processors.repos import ReposProcessor
from dev_observer.processors.websites import WebsitesProcessor, ObservedWebsite
from dev_observer.repository.types import ObservedRepo
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import Clock, RealClock
from dev_observer.website.cloner import normalize_domain, normalize_name

_log = logging.getLogger(__name__)


class PeriodicProcessor:
    _storage: StorageProvider
    _repos_processor: ReposProcessor
    _aggregated_summary_processor: AggregatedSummaryProcessor
    _git_changes_handler: GitChangesHandler
    _websites_processor: Optional[WebsitesProcessor]
    _clock: Clock

    def __init__(self,
                 storage: StorageProvider,
                 repos_processor: ReposProcessor,
                 aggregated_summary_processor: AggregatedSummaryProcessor,
                 git_changes_handler: GitChangesHandler,
                 websites_processor: Optional[WebsitesProcessor] = None,
                 clock: Clock = RealClock(),
                 ):
        self._storage = storage
        self._repos_processor = repos_processor
        self._git_changes_handler = git_changes_handler
        self._aggregated_summary_processor = aggregated_summary_processor
        self._websites_processor = websites_processor
        self._clock = clock

    async def run(self):
        # TODO: add proper background processing
        _log.info("Starting periodic processor")
        while True:
            try:
                await self.process_next()
            except Exception as e:
                _log.error(s_("Failed to process next item"), exc_info=e)
            await asyncio.sleep(2)

    async def process_next(self) -> Optional[ProcessingItem]:
        item = await self._storage.next_processing_item()
        if item is None:
            return None
        _log.info(s_("Processing item", item=item))
        retry_time = self._clock.now() + timedelta(minutes=30)
        # prevent from running again right away.
        await self._storage.set_next_processing_time(item.key, retry_time, processing_started_at=self._clock.now())
        try:
            result = await self._process_item(item)
            _log.info(s_("Item processed", item=item))
        except TerminalError as e:
            _log.exception(s_("Failed to process item due to terminal error, deleting", item=item, err=e))
            await self._finalize_execution(item, ProcessingItemResultData(), error=f"Terminal error: {e}")
            raise
        except Exception as e:
            await self._finalize_execution(item, None, error=f"{e}")
            raise
        await self._finalize_execution(item, result)
        _log.debug(s_("Item execution finalized", item=item, result=result))
        return item

    async def _finalize_execution(
            self,
            item: ProcessingItem,
            result_data: Optional[ProcessingItemResultData],
            error: Optional[str] = None,
    ):
        ent_type = item.key.WhichOneof("entity")
        try:
            if result_data is not None:
                await self._storage.add_processing_result(ProcessingItemResult(
                    id=item.key.request_id,
                    key=item.key,
                    error_message=error,
                    result_data=result_data,
                    data=item.data,
                ))
                if ent_type == "request_id":
                    await self._storage.delete_processing_item(item.key)
                if ent_type == "periodic_aggregation_id":
                    await self._finalize_periodic_aggregation(item.key, item.data.periodic_aggregation)
                else:
                    await self._storage.set_next_processing_time(item.key, None, error)
            else:
                # If result_data is none, keep retrying periodically. That means processing is not enabled yet.
                if error:
                    await self._storage.set_processing_error(item.key, error)
        except TerminalError as e:
            _log.exception(s_("Failed to finalize execution due to terminal error, deleting", item=item, err=e))
            await self._storage.set_next_processing_time(item.key, None, f"{e}")

    async def _finalize_periodic_aggregation(self, key: ProcessingItemKey, aggregation: PeriodicAggregation):
        if not aggregation.HasField("schedule"):
            raise TerminalError("Schedule not provided")
        old_end = pb_to_datetime(aggregation.params.end_date)
        try:
            next_date = get_next_date(old_end, aggregation.schedule)
        except Exception as e:
            raise TerminalError(f"Failed to compute next run: {e}")
        next_processing = next_date if self._clock.now() < next_date else self._clock.now() + timedelta(seconds=5)

        def updater(db_item: ProcessingItem):
            db_item.data.periodic_aggregation.params.end_date = next_date
            return db_item

        await self._storage.update_processing_item(key, updater, next_processing)

    async def _process_item(self, item: ProcessingItem) -> Optional[ProcessingItemResultData]:
        ent_type = item.key.WhichOneof("entity")
        if ent_type == "github_repo_id":
            return await self._process_github_repo(item.key.github_repo_id)
        elif ent_type == "website_url":
            if self._websites_processor is None:
                _log.error(s_("Website processor is not configured", url=item.key.website_url))
                raise ValueError(f"Website processor is not configured")
            return await self._process_website(item.key.website_url)
        elif ent_type == "request_id":
            if not item.HasField("data") or not item.data.HasField("request"):
                raise TerminalError(f"Request not defined for request id {item.key.request_id}")
            return await self._process_request(item.data.request)
        elif ent_type == "periodic_aggregation_id":
            if not item.HasField("data") or not item.data.HasField("periodic_aggregation"):
                raise TerminalError(
                    f"Periodic aggregation not defined for aggregation id {item.key.periodic_aggregation_id}")
            return await self._process_periodic_aggregation(
                item.key.periodic_aggregation_id, item.data.periodic_aggregation)
        else:
            raise ValueError(f"[{ent_type}] is not supported")

    async def _process_github_repo(self, repo_id: str) -> Optional[ProcessingItemResultData]:
        config = await self._storage.get_global_config()
        if config.HasField("repo_analysis") and config.repo_analysis.disabled:
            _log.warning(s_("Repo analysis disabled"))
            return None

        repo = await self._storage.get_git_repo(repo_id)
        if repo is None:
            _log.error(s_("Github repo not found", repo_id=repo_id))
            raise ValueError(f"Repo with id [{repo_id}] is not found")
        _log.debug(s_("Processing github repo", repo=repo))
        requests: List[ObservationRequest] = []
        for analyzer in config.analysis.repo_analyzers:
            key = f"{repo.full_name}/{analyzer.file_name}"
            requests.append(ObservationRequest(
                prompt_prefix=analyzer.prompt_prefix,
                key=ObservationKey(kind="repos", name=analyzer.file_name, key=key),
            ))
        if len(requests) == 0:
            _log.debug(s_("No analyzers configured, skipping", repo=repo))
            return None
        return await self._repos_processor.process(ObservedRepo(url=repo.url, git_repo=repo), requests, config)

    async def _process_website(self, website_url: str) -> Optional[ProcessingItemResultData]:
        _log.debug(s_("Processing website", url=website_url))
        requests: List[ObservationRequest] = []
        config = await self._storage.get_global_config()

        for analyzer in config.analysis.site_analyzers:
            domain = normalize_domain(website_url)
            name = normalize_name(website_url)
            key = f"{domain}/{name}/{analyzer.file_name}"

            requests.append(ObservationRequest(
                prompt_prefix=analyzer.prompt_prefix,
                key=ObservationKey(kind="websites", name=analyzer.file_name, key=key),
            ))

        if len(requests) == 0:
            _log.debug(s_("No analyzers configured, skipping", url=website_url))
            return None

        return await self._websites_processor.process(ObservedWebsite(url=website_url), requests, config)

    async def _process_request(self, req: ProcessingRequest):
        req_type = req.WhichOneof("type")
        if req_type == "git_changes":
            return await self._process_git_changes(req.git_changes)
        else:
            raise ValueError(f"[{req_type}] is not supported")

    async def _process_git_changes(self, req: ProcessGitChangesRequest) -> Optional[List[ObservationKey]]:
        res = await self._git_changes_handler.process_git_changes(ProcessGitChangesParams(
            end_date=self._clock.now(),
            look_back_days=req.look_back_days,
            repo_id=req.git_repo_id,
        ))
        return res.observation_keys if res else None

    async def _process_periodic_aggregation(
            self, aggregation_id: str, req: PeriodicAggregation) -> Optional[ProcessingItemResultData]:
        config = await self._storage.get_global_config()
        if not config.analysis.HasField("default_aggregated_summary_analyzer"):
            _log.warning(s_("Aggregated summary disabled"))
            return None
        analyzer = config.analysis.default_aggregated_summary_analyzer
        params = req.params
        end_date = pb_to_datetime(params.end_date)
        period_str = f"{end_date.strftime('%Y%m%dT%H%M')}_{params.look_back_days}d"
        key = ObservationKey(
            kind="aggregated_summary",
            name=analyzer.file_name,
            key=f"{aggregation_id}/{period_str}/{analyzer.file_name}",
        )
        obs_request = ObservationRequest(prompt_prefix=analyzer.prompt_prefix, key=key)
        extra = {
            "op": "process_periodic_aggregation",
            "aggregation_id": aggregation_id,
            "params": params,
            "request": obs_request,
        }
        _log.info(s_("Starting", **extra))
        result = await self._aggregated_summary_processor.process(params, [obs_request], config)
        _log.info(s_("Processed", **extra))
        return result
