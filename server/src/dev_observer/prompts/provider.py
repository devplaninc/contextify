import dataclasses
from abc import abstractmethod
from typing import Protocol, Optional, Dict

from langfuse.model import ChatPromptClient

from dev_observer.api.types.ai_pb2 import PromptConfig, SystemMessage, UserMessage


@dataclasses.dataclass
class FormattedPrompt:
    config: Optional[PromptConfig]
    system: Optional[SystemMessage]
    user: Optional[UserMessage]
    langfuse_prompt: Optional[ChatPromptClient] = None
    prompt_name: Optional[str] = None


class PromptsProvider(Protocol):
    @abstractmethod
    async def get_formatted(self, name: str, params: Optional[Dict[str, str]] = None) -> FormattedPrompt:
        ...

    @abstractmethod
    async def get_optional(self, name: str, params: Optional[Dict[str, str]] = None) -> Optional[FormattedPrompt]:
        ...


class PrefixedPromptsFetcher:
    provider: PromptsProvider

    def __init__(self, provider: PromptsProvider):
        self.provider = provider

    async def get(self, prefix: str, suffix: str, params: Optional[Dict[str, str]] = None) -> FormattedPrompt:
        return await self.provider.get_formatted(f"{prefix}_{suffix}", params)