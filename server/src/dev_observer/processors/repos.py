from typing import Optional

from dev_observer.analysis.provider import AnalysisProvider
from dev_observer.api.types.config_pb2 import GlobalConfig
from dev_observer.flatten.flatten import flatten_repository, FlattenResult
from dev_observer.observations.provider import ObservationsProvider
from dev_observer.processors.flattening import FlatteningProcessor
from dev_observer.prompts.provider import PromptsProvider
from dev_observer.repository.provider import GitRepositoryProvider
from dev_observer.repository.tokens import persist_repo_tokens_info_async
from dev_observer.repository.types import ObservedRepo
from dev_observer.storage.provider import StorageProvider
from dev_observer.tokenizer.provider import TokenizerProvider


class ReposProcessor(FlatteningProcessor[ObservedRepo]):
    repository: GitRepositoryProvider
    storage: Optional[StorageProvider]

    def __init__(
            self,
            analysis: AnalysisProvider,
            repository: GitRepositoryProvider,
            prompts: PromptsProvider,
            observations: ObservationsProvider,
            tokenizer: TokenizerProvider,
            storage: Optional[StorageProvider] = None,
    ):
        super().__init__(analysis, prompts, observations, tokenizer)
        self.repository = repository
        self.storage = storage

    async def get_flatten(self, repo: ObservedRepo, config: GlobalConfig) -> FlattenResult:
        res = await flatten_repository(repo, self.repository, self.tokenizer, config)
        persist_repo_tokens_info_async(self.storage, repo.git_repo, res.flatten_result.total_tokens)
        return res.flatten_result
