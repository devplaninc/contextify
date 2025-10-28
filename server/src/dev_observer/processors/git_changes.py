from dev_observer.analysis.provider import AnalysisProvider
from dev_observer.api.types.config_pb2 import GlobalConfig
from dev_observer.flatten.flatten import FlattenResult, flatten_repo_changes
from dev_observer.observations.provider import ObservationsProvider
from dev_observer.processors.flattening import FlatteningProcessor
from dev_observer.prompts.provider import PromptsProvider
from dev_observer.repository.provider import GitRepositoryProvider
from dev_observer.repository.tokens import persist_repo_tokens_info_async
from dev_observer.repository.types import ObservedGitChanges
from dev_observer.storage.provider import StorageProvider
from dev_observer.tokenizer.provider import TokenizerProvider


class GitChangesProcessor(FlatteningProcessor[ObservedGitChanges]):
    repository: GitRepositoryProvider
    tokenizer: TokenizerProvider
    storage: StorageProvider

    def __init__(
            self,
            analysis: AnalysisProvider,
            repository: GitRepositoryProvider,
            prompts: PromptsProvider,
            observations: ObservationsProvider,
            tokenizer: TokenizerProvider,
            storage: StorageProvider,
    ):
        super().__init__(analysis, prompts, observations)
        self.repository = repository
        self.tokenizer = tokenizer
        self.storage = storage

    async def get_flatten(self, params: ObservedGitChanges, config: GlobalConfig) -> FlattenResult:
        res = await flatten_repo_changes(params, self.repository, self.tokenizer, config)
        persist_repo_tokens_info_async(self.storage, params.repo.git_repo, res.flatten_result.total_tokens)
        return res.flatten_result
