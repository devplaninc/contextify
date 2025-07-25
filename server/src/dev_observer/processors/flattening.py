import abc
import dataclasses
import logging
from abc import abstractmethod
from typing import TypeVar, Generic, List

from dev_observer.analysis.provider import AnalysisProvider
from dev_observer.api.types.config_pb2 import GlobalConfig
from dev_observer.api.types.observations_pb2 import ObservationKey, Observation
from dev_observer.flatten.flatten import FlattenResult
from dev_observer.log import s_
from dev_observer.observations.provider import ObservationsProvider
from dev_observer.processors.tokenized import TokenizedAnalyzer
from dev_observer.prompts.provider import PromptsProvider

E = TypeVar("E")

_log = logging.getLogger(__name__)


@dataclasses.dataclass
class ObservationRequest:
    prompt_prefix: str
    key: ObservationKey


class FlatteningProcessor(abc.ABC, Generic[E]):
    analysis: AnalysisProvider
    prompts: PromptsProvider
    observations: ObservationsProvider

    def __init__(
            self,
            analysis: AnalysisProvider,
            prompts: PromptsProvider,
            observations: ObservationsProvider,
    ):
        self.analysis = analysis
        self.prompts = prompts
        self.observations = observations

    async def process(
            self, entity: E, requests: List[ObservationRequest], config: GlobalConfig, clean: bool = True,
    ) -> List[ObservationKey]:
        res = await self.get_flatten(entity, config)
        _log.debug(s_("Got flatten result", result=res))
        try:
            result: List[ObservationKey] = []
            for request in requests:
                try:
                    prompts_prefix = request.prompt_prefix
                    key = request.key
                    analyzer = TokenizedAnalyzer(prompts_prefix=prompts_prefix, analysis=self.analysis,
                                                 prompts=self.prompts)
                    content = await analyzer.analyze_flatten(res)
                    await self.observations.store(Observation(key=key, content=content))
                    result.append(key)
                except Exception as e:
                    _log.exception(s_("Analysis failed.", request=request), exc_info=e)
            if res.extra_keys:
                result.extend(res.extra_keys)
            return result
        finally:
            if clean:
                res.clean_up()

    @abstractmethod
    async def get_flatten(self, entity: E, config: GlobalConfig) -> FlattenResult:
        pass
