import logging
from typing import Optional, Tuple, Literal, ClassVar, List

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource, TomlConfigSettingsSource

from dev_observer.log import s_

_log = logging.getLogger(__name__)


class Github(BaseModel):
    auth_type: Literal["token", "app"]
    personal_token: Optional[str] = None
    app_id: Optional[str] = None
    private_key: Optional[str] = None


class Git(BaseModel):
    provider: Literal["github", "copying", "delegating", "federated"] = "github"

    github: Optional[Github] = None


class LangfuseAuth(BaseModel):
    secret_key: str
    public_key: str


class LangfusePrompts(BaseModel):
    auth: LangfuseAuth
    host: str
    default_label: Optional[str] = None
    mask_traces: bool = True


class LocalPrompts(BaseModel):
    dir: str
    parser: Literal["toml", "json"] = "toml"


class Prompts(BaseModel):
    provider: Literal["langfuse", "local"]
    langfuse: Optional[LangfusePrompts] = None
    local: Optional[LocalPrompts] = None


class LanggraphAnalysis(BaseModel):
    ...


class Analysis(BaseModel):
    provider: Literal["langgraph", "stub"] = "langgraph"

    langgrpah: Optional[LanggraphAnalysis] = None


class LocalObservations(BaseModel):
    dir: str


class S3Observations(BaseModel):
    endpoint: str
    access_key: str
    secret_key: str
    bucket: str
    region: str


class GCSObservations(BaseModel):
    bucket: str


class Observations(BaseModel):
    provider: Literal["local", "s3", "gcs"] = "local"

    local: Optional[LocalObservations] = None
    s3: Optional[S3Observations] = None
    gcs: Optional[GCSObservations] = None


class SettingsProps(BaseModel):
    toml_file: Optional[str] = None


class Tiktoken(BaseModel):
    encoding: str = "cl100k_base"


class Tokenizer(BaseModel):
    provider: Literal["tiktoken", "stub"] = "tiktoken"

    tiktoken: Optional[Tiktoken] = None


class LocalStorage(BaseModel):
    dir: str


class PostgresqlStorage(BaseModel):
    db_url: str


class Storage(BaseModel):
    provider: Literal["local", "memory", "postgresql"] = "postgresql"

    local: Optional[LocalStorage] = None
    postgresql: Optional[PostgresqlStorage] = None


class Clerk(BaseModel):
    public_key: str
    secret_key: str


class ApiKeys(BaseModel):
    keys: Optional[List[str]] = None


class UserManagement(BaseModel):
    provider: Literal["clerk", "none"] = "none"
    clerk: Optional[Clerk] = None


class WebScraping(BaseModel):
    provider: Literal["scrapy"] = "scrapy"


class Crypto(BaseModel):
    secret: str


class Settings(BaseSettings):
    props: ClassVar[SettingsProps] = SettingsProps()

    git: Optional[Git] = None
    prompts: Optional[Prompts] = None
    analysis: Optional[Analysis] = None
    observations: Optional[Observations] = None
    tokenizer: Optional[Tokenizer] = None
    storage: Optional[Storage] = None
    users_management: Optional[UserManagement] = None
    api_keys: Optional[ApiKeys] = None
    web_scraping: Optional[WebScraping] = WebScraping()
    crypto: Optional[Crypto] = None

    def __init__(self) -> None:
        toml_file = Settings.model_config.get("toml_file", None)
        Settings.model_config = SettingsConfigDict(
            env_prefix='dev_observer__',
            env_nested_delimiter='__',
            toml_file=toml_file,
        )
        super().__init__()

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        toml_file = Settings.model_config.get("toml_file", None)
        _log.debug(s_("Loading settings", toml_file=toml_file))
        if toml_file is not None:
            toml_provider = TomlConfigSettingsSource(Settings, toml_file)
            return init_settings, toml_provider, env_settings, dotenv_settings, file_secret_settings
        return init_settings, env_settings, dotenv_settings, file_secret_settings
