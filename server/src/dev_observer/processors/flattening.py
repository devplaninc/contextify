import abc
import dataclasses
import logging
from abc import abstractmethod
from datetime import date
from typing import TypeVar, Generic, List, Optional

from dev_observer.analysis.provider import AnalysisProvider
from dev_observer.api.types.config_pb2 import GlobalConfig
from dev_observer.api.types.observations_pb2 import ObservationKey, Observation
from dev_observer.api.types.processing_pb2 import ProcessingItemResultData
from dev_observer.flatten.flatten import FlattenResult
from dev_observer.log import s_
from dev_observer.observations.provider import ObservationsProvider
from dev_observer.processors.tokenized import TokenizedAnalyzer
from dev_observer.prompts.provider import PromptsProvider
from dev_observer.tokenizer.provider import TokenizerProvider

E = TypeVar("E")

_log = logging.getLogger(__name__)


@dataclasses.dataclass
class ObservationRequest:
    prompt_prefix: str
    key: ObservationKey
    summary_key: Optional[ObservationKey] = None  # If set, instructs to also produce a summary for the observation.


class FlatteningProcessor(abc.ABC, Generic[E]):
    analysis: AnalysisProvider
    prompts: PromptsProvider
    observations: ObservationsProvider
    tokenizer: TokenizerProvider

    def __init__(
            self,
            analysis: AnalysisProvider,
            prompts: PromptsProvider,
            observations: ObservationsProvider,
            tokenizer: TokenizerProvider
    ):
        self.analysis = analysis
        self.prompts = prompts
        self.observations = observations
        self.tokenizer = tokenizer

    async def process(
            self, entity: E, requests: List[ObservationRequest], config: GlobalConfig, clean: bool = True,
    ) -> ProcessingItemResultData:
        res = await self.get_flatten(entity, config)
        _log.debug(s_("Got flatten result", result=res))
        try:
            keys: List[ObservationKey] = []
            for request in requests:
                try:
                    prompts_prefix = request.prompt_prefix
                    key = request.key
                    summary_tokens_limit = await self.get_summary_tokens_limit(config)
                    analyzer = TokenizedAnalyzer(
                        prompts_prefix=prompts_prefix,
                        analysis=self.analysis,
                        prompts=self.prompts,
                        summary_tokens_limit=summary_tokens_limit,
                        tokenizer=self.tokenizer,
                    )
                    content = await analyzer.analyze_flatten(res)
                    await self.observations.store(Observation(key=key, content=content))
                    keys.append(key)
                    sum_key = await self._summarize(request, content, res)
                    if sum_key:
                        keys.append(sum_key)
                except Exception as e:
                    _log.exception(s_("Analysis failed.", request=request), exc_info=e)
            result_data = res.result_data
            if result_data is None:
                result_data = ProcessingItemResultData()
            result_data.observations.extend(keys)
            return result_data
        finally:
            if clean:
                res.clean_up()

    async def _summarize(
            self, request: ObservationRequest, content: str, flatten_result: FlattenResult,
    ) -> Optional[ObservationKey]:
        sum_key = request.summary_key
        if not sum_key:
            return None
        try:
            prompt_name = f"{request.prompt_prefix}_summarize_analysis"
            prompt = await self.prompts.get_optional(prompt_name, {"content": content})
            if prompt is None:
                _log.debug(s_("No analysis summary configured", prompt_name=prompt_name))
                return None
            session_id = f"{date.today().strftime("%Y-%m-%d")}.{flatten_result.full_file_path}"
            result = await self.analysis.analyze(prompt, session_id)
            await self.observations.store(Observation(key=sum_key, content=result.analysis))
            return sum_key
        except Exception as e:
            _log.exception(s_("Summarization failed.", request=request), exc_info=e)
            return None

    async def get_summary_tokens_limit(self, config: GlobalConfig) -> int:
        return 800000

    @abstractmethod
    async def get_flatten(self, entity: E, config: GlobalConfig) -> FlattenResult:
        pass
