import asyncio
import logging
from datetime import timedelta
from typing import List, Optional

from dev_observer.api.types.observations_pb2 import ObservationKey
from dev_observer.api.types.processing_pb2 import ProcessingItem, ProcessingRequest, ProcessGitChangesRequest, \
    ProcessingItemResult, ProcessingItemKey, PeriodicAggregation
from dev_observer.common.errors import TerminalError
from dev_observer.common.schedule import get_next_date
from dev_observer.log import s_
from dev_observer.processors.flattening import ObservationRequest
from dev_observer.processors.git.changes import GitChangesHandler, ProcessGitChangesParams
from dev_observer.processors.git_changes import GitChangesProcessor
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
    _git_changes_handler: GitChangesHandler
    _websites_processor: Optional[WebsitesProcessor]
    _clock: Clock

    def __init__(self,
                 storage: StorageProvider,
                 repos_processor: ReposProcessor,
                 git_changes_processor: GitChangesProcessor,
                 websites_processor: Optional[WebsitesProcessor] = None,
                 clock: Clock = RealClock(),
                 ):
        self._storage = storage
        self._repos_processor = repos_processor
        self._git_changes_handler = GitChangesHandler(
            git_changes_processor=git_changes_processor,
            storage=storage,
            observations=repos_processor.observations,
            clock=clock,
        )
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
            await self._finalize_execution(item, [], error=f"Terminal error: {e}")
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
            result: Optional[List[ObservationKey]],
            error: Optional[str] = None,
    ):
        ent_type = item.key.WhichOneof("entity")
        if result is not None:
            await self._storage.add_processing_result(ProcessingItemResult(
                id=item.key.request_id,
                key=item.key,
                error_message=error,
                observations=result,
                request=item.request if item.HasField("request") else None,
            ))
            if ent_type == "request_id":
                await self._storage.delete_processing_item(item.key)
            if ent_type == "periodic_aggregation_id":
                await self._schedule_periodic(item.key, item.periodic_aggregation)
            else:
                await self._storage.set_next_processing_time(item.key, None, error)
        else:
            if error:
                await self._storage.set_processing_error(item.key, error)

    async def _schedule_periodic(
            self, key: ProcessingItemKey, item: PeriodicAggregation) -> Optional[List[ObservationKey]]:
        if not item.HasField("schedule"):
            raise TerminalError("Schedule not provided")
        try:
            next_date = get_next_date(item.params.end_date, item.schedule)
        except Exception as e:
            raise TerminalError(f"Failed to compute next run: {e}")
        item.params.end_date = next_date
        next_processing = next_date if self._clock.now() < next_date else self._clock.now() + timedelta(seconds=5)

        def updater(db_item: ProcessingItem):
            db_item.periodic_aggregation.CopyFrom(item)

        await self._storage.update_processing_item(key, updater, next_processing)

    async def _process_item(self, item: ProcessingItem) -> Optional[List[ObservationKey]]:
        ent_type = item.key.WhichOneof("entity")
        if ent_type == "github_repo_id":
            return await self._process_github_repo(item.key.github_repo_id)
        elif ent_type == "website_url":
            if self._websites_processor is None:
                _log.error(s_("Website processor is not configured", url=item.key.website_url))
                raise ValueError(f"Website processor is not configured")
            return await self._process_website(item.key.website_url)
        elif ent_type == "request_id":
            if not item.HasField("request"):
                raise TerminalError(f"Request not defined for request id {item.key.request_id}")
            return await self._process_request(item.request)
        else:
            raise ValueError(f"[{ent_type}] is not supported")

    async def _process_github_repo(self, repo_id: str) -> Optional[List[ObservationKey]]:
        config = await self._storage.get_global_config()
        if config.HasField("repo_analysis") and config.repo_analysis.disabled:
            _log.warning(s_("Repo analysis disabled"))
            return None

        repo = await self._storage.get_github_repo(repo_id)
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
        return await self._repos_processor.process(ObservedRepo(url=repo.url, github_repo=repo), requests, config)

    async def _process_website(self, website_url: str) -> Optional[List[ObservationKey]]:
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
