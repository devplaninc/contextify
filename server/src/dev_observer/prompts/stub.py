from typing import Optional, Dict

from dev_observer.api.types.ai_pb2 import SystemMessage, UserMessage, PromptConfig, ModelConfig
from dev_observer.prompts.provider import PromptsProvider, FormattedPrompt


class StubPromptsProvider(PromptsProvider):
    async def get_formatted(self, name: str, params: Optional[Dict[str, str]] = None) -> FormattedPrompt:
        return FormattedPrompt(
            system=SystemMessage(text="Stub system message"),
            user=UserMessage(text="Stub user message"),
            config=PromptConfig(model=ModelConfig(provider="openai", model_name="test", temperature=0)),
        )

    async def get_optional(self, name: str, params: Optional[Dict[str, str]] = None) -> Optional[FormattedPrompt]:
        return await self.get_formatted(name, params)


