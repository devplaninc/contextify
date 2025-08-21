import logging
from typing import Optional, Tuple, Dict

from dev_observer.analysis.code.graph import create_code_research_graph
from dev_observer.analysis.langgraph_provider import LanggraphAnalysisProvider
from dev_observer.analysis.provider import AnalysisProvider
from dev_observer.analysis.stub import StubAnalysisProvider
from dev_observer.api.types.repo_pb2 import GitProvider
from dev_observer.common.crypto import Encryptor
from dev_observer.log import s_
from dev_observer.observations.local import LocalObservationsProvider
from dev_observer.observations.provider import ObservationsProvider
from dev_observer.observations.s3 import S3ObservationsProvider
from dev_observer.processors.aggregated_summary import AggregatedSummaryProcessor
from dev_observer.processors.code_research import CodeResearchProcessor
from dev_observer.processors.git.changes import GitChangesHandler
from dev_observer.processors.git_changes import GitChangesProcessor
from dev_observer.processors.periodic import PeriodicProcessor
from dev_observer.processors.repos import ReposProcessor
from dev_observer.processors.websites import WebsitesProcessor
from dev_observer.prompts.langfuse import LangfusePromptsProvider, LangfuseAuthProps
from dev_observer.prompts.local import LocalPromptsProvider, PromptTemplateParser, TomlPromptTemplateParser, \
    JSONPromptTemplateParser
from dev_observer.prompts.provider import PromptsProvider
from dev_observer.repository.auth.bitbucket_token import BitBucketTokenAuthProvider
from dev_observer.repository.auth.github_token import GithubTokenAuthProvider
from dev_observer.repository.bitbucket import BitBucketProvider
from dev_observer.repository.copying import CopyingGitRepositoryProvider
from dev_observer.repository.delegating import DelegatingGitRepositoryProvider
from dev_observer.repository.federated import FederatedGitProvider
from dev_observer.repository.github import GithubProvider, GithubAuthProvider
from dev_observer.repository.provider import GitRepositoryProvider
from dev_observer.server.env import ServerEnv
from dev_observer.settings import Settings, LocalPrompts, Github, LangfusePrompts, LanggraphAnalysis, Git
from dev_observer.storage.local import LocalStorageProvider
from dev_observer.storage.memory import MemoryStorageProvider
from dev_observer.storage.postgresql.provider import PostgresqlStorageProvider
from dev_observer.storage.provider import StorageProvider
from dev_observer.tokenizer.provider import TokenizerProvider
from dev_observer.tokenizer.stub import StubTokenizerProvider
from dev_observer.tokenizer.tiktoken import TiktokenTokenizerProvider
from dev_observer.users.clerk import ClerkUsersProvider
from dev_observer.users.no_auth import NoAuthUsersProvider
from dev_observer.users.provider import UsersProvider
from dev_observer.website.crawler import ScrapyWebsiteCrawlerProvider
from dev_observer.website.provider import WebsiteCrawlerProvider

_log = logging.getLogger(__name__)


def detect_git_provider(settings: Settings, storage: StorageProvider) -> GitRepositoryProvider:
    git_sett = settings.git
    if git_sett is None:
        raise ValueError("Git settings are not provided")
    match git_sett.provider:
        case "github":
            return create_github_provider(git_sett.github, storage)
        case "copying":
            return CopyingGitRepositoryProvider()
        case "delegating":
            return DelegatingGitRepositoryProvider()
        case "federated":
            return create_federated_git_provider(git_sett, storage)
    raise ValueError(f"Unsupported git provider: {git_sett.provider}")

def create_github_provider(gh_sett: Github, storage: StorageProvider) -> GithubProvider:
    return GithubProvider(detect_github_auth(gh_sett, storage), storage)


def create_federated_git_provider(git_sett: Git, storage: StorageProvider) -> FederatedGitProvider:
    providers: Dict[GitProvider, GitRepositoryProvider] = {
        GitProvider.BIT_BUCKET: BitBucketProvider(BitBucketTokenAuthProvider(storage), storage),
    }
    if git_sett.github is not None:
        providers[GitProvider.GITHUB] = create_github_provider(git_sett.github, storage)
    return FederatedGitProvider(providers)

def detect_github_auth(gh: Optional[Github], storage: StorageProvider) -> GithubAuthProvider:
    if gh is None:
        raise ValueError(f"Github settings are not defined")
    _log.debug(s_("Detected github auth type.", auth_type=gh.auth_type))
    match gh.auth_type:
        case "token":
            return GithubTokenAuthProvider(gh.personal_token)
        case "app":
            from dev_observer.repository.auth import GithubAppAuthProvider
            if not gh.app_id or not gh.private_key:
                raise ValueError("GitHub App authentication requires app_id and private_key")
            return GithubAppAuthProvider(gh.app_id, gh.private_key, storage)
    raise ValueError(f"Unsupported auth type: {gh.auth_type}")


def detect_analysis_provider(settings: Settings, storage: StorageProvider) -> AnalysisProvider:
    a = settings.analysis
    if a is None:
        raise ValueError("Analysis settings are not defined")
    match a.provider:
        case "langgraph":
            lg = a.langgrpah if a.langgrpah is not None else LanggraphAnalysis()
            lf_auth: Optional[LangfuseAuthProps] = None
            if settings.prompts is not None and settings.prompts.langfuse is not None:
                lf_auth = _get_lf_auth(settings.prompts.langfuse)
            return LanggraphAnalysisProvider(storage, lf_auth, mask=lg.mask_traces)
        case "stub":
            return StubAnalysisProvider()
    raise ValueError(f"Unsupported analysis provider: {a.provider}")


def detect_prompts_provider(settings: Settings) -> PromptsProvider:
    p = settings.prompts
    if p is None:
        raise ValueError("Prompts settings are not defined")
    match p.provider:
        case "langfuse":
            lf = p.langfuse
            if lf is None:
                raise ValueError("Missing langfuse config for langfuse prompts provider")
            return LangfusePromptsProvider(_get_lf_auth(lf), lf.default_label)
        case "local":
            parser, ext = detect_prompts_parser(p.local)
            return LocalPromptsProvider(p.local.dir, ext, parser)
    raise ValueError(f"Unsupported prompts provider: {p.provider}")


def _get_lf_auth(lf: LangfusePrompts) -> LangfuseAuthProps:
    return LangfuseAuthProps(
        secret_key=lf.auth.secret_key,
        public_key=lf.auth.public_key,
        host=lf.host,
    )


def detect_prompts_parser(loc: LocalPrompts) -> Tuple[PromptTemplateParser, str]:
    match loc.parser:
        case "toml":
            return TomlPromptTemplateParser(), ".toml"
        case "json":
            return JSONPromptTemplateParser(), ".json"
    raise ValueError(f"Unsupported parser type: {loc.parser}")


def detect_observer(settings: Settings) -> ObservationsProvider:
    o = settings.observations
    if o is None:
        raise ValueError("Observations settings are not defined")
    match o.provider:
        case "local":
            if o.local is None:
                raise ValueError("Missing local config for local observations provider")
            return LocalObservationsProvider(root_dir=o.local.dir)
        case "s3":
            if o.s3 is None:
                raise ValueError("Missing S3 config for S3 observations provider")
            try:
                return S3ObservationsProvider(
                    endpoint=o.s3.endpoint,
                    access_key=o.s3.access_key,
                    secret_key=o.s3.secret_key,
                    bucket=o.s3.bucket,
                    region=o.s3.region
                )
            except ValueError as e:
                # Re-raise with more context
                raise ValueError(f"Failed to initialize S3 observations provider: {str(e)}") from e
    raise ValueError(f"Unsupported observations provider: {o.provider}")


def detect_tokenizer(settings: Settings) -> TokenizerProvider:
    tok = settings.tokenizer
    match tok.provider:
        case "tiktoken":
            return TiktokenTokenizerProvider(encoding=tok.tiktoken.encoding)
        case "stub":
            return StubTokenizerProvider()
    raise ValueError(f"Unsupported tokenizer provider: {tok.provider}")


def detect_storage_provider(settings: Settings) -> StorageProvider:
    s = settings.storage
    if s is None:
        raise ValueError("Storage settings are not defined")
    match s.provider:
        case "memory":
            return MemoryStorageProvider()
        case "postgresql":
            return PostgresqlStorageProvider(s.postgresql.db_url, Encryptor(settings.crypto.secret))
        case "local":
            return LocalStorageProvider(s.local.dir)
    raise ValueError(f"Unsupported storage provider: {s.provider}")


def detect_users_provider(settings: Settings) -> UsersProvider:
    u = settings.users_management
    if u is None:
        return NoAuthUsersProvider()
    match u.provider:
        case "clerk":
            return ClerkUsersProvider(u.clerk.secret_key, u.clerk.public_key)
        case "none":
            return NoAuthUsersProvider()
    raise ValueError(f"Unsupported users management provider: {u.provider}")


def detect_web_scraping(settings: Settings) -> WebsiteCrawlerProvider:
    ws = settings.web_scraping
    if ws is None:
        raise ValueError(f"Web scraping provider is not specified")
    match ws.provider:
        case "scrapy":
            return ScrapyWebsiteCrawlerProvider()
    raise ValueError(f"Unsupported web scraping provider: {ws.provider}")


def detect_server_env(settings: Settings) -> ServerEnv:
    prompts = detect_prompts_provider(settings)
    observations = detect_observer(settings)
    tokenizer = detect_tokenizer(settings)
    storage = detect_storage_provider(settings)
    analysis = detect_analysis_provider(settings, storage)
    bg_storage = detect_storage_provider(settings)
    bg_analysis = detect_analysis_provider(settings, bg_storage)
    bg_repository = detect_git_provider(settings, bg_storage)
    bg_repos_processor = ReposProcessor(bg_analysis, bg_repository, prompts, observations, tokenizer)
    bg_git_changes_processor = GitChangesProcessor(bg_analysis, bg_repository, prompts, observations, tokenizer)
    bg_web_scraping = detect_web_scraping(settings)
    bg_sites_processor = WebsitesProcessor(bg_analysis, bg_web_scraping, prompts, observations, tokenizer)
    bg_git_changes_handler = GitChangesHandler(bg_git_changes_processor, bg_storage, observations)
    bg_agg_summary_processor = AggregatedSummaryProcessor(
        bg_analysis, bg_repository, prompts, observations, tokenizer, bg_git_changes_handler, bg_storage)
    users = detect_users_provider(settings)
    research_graph = create_code_research_graph(prompts, tokenizer, bg_storage)

    bg_research_processor = CodeResearchProcessor(
        research_graph, bg_repository, bg_storage, observations
    )

    # Extract API key from settings if available
    api_keys = None
    if settings.api_keys:
        api_keys = settings.api_keys.keys
        if api_keys:
            _log.info(s_("API key authentication enabled"))

    env = ServerEnv(
        observations=observations,
        storage=storage,
        prompts=prompts,
        analysis=analysis,
        repos_processor=bg_repos_processor,
        periodic_processor=PeriodicProcessor(
            bg_storage,
            bg_repos_processor,
            bg_agg_summary_processor,
            bg_git_changes_handler,
            websites_processor=bg_sites_processor,
            research_processor=bg_research_processor,
        ),
        users=users,
        api_keys=api_keys or [],
    )
    _log.debug(s_("Detected environment",
                  bg_repository=bg_repository,
                  analysis=bg_analysis,
                  prompts=prompts,
                  observations=observations,
                  users=users,
                  env=env))
    return env
