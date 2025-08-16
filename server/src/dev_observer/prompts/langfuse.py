import dataclasses
import logging
from typing import Optional, Dict, cast

from langfuse import Langfuse
from langfuse.model import ChatPromptClient

from dev_observer.api.types.ai_pb2 import PromptConfig, SystemMessage, UserMessage
from dev_observer.log import s_
from dev_observer.prompts.provider import PromptsProvider, FormattedPrompt
from dev_observer.util import parse_dict_pb

_log = logging.getLogger(__name__)

@dataclasses.dataclass
class LangfuseAuthProps:
    secret_key: str
    public_key: str
    host: str


class LangfusePromptsProvider(PromptsProvider):
    _langfuse: Langfuse
    _default_label: Optional[str] = None

    def __init__(self, auth: LangfuseAuthProps, default_label: Optional[str] = None):
        self._default_label = default_label
        self._langfuse = Langfuse(secret_key=auth.secret_key, public_key=auth.public_key, host=auth.host)

    async def get_formatted(self, name: str, params: Optional[Dict[str, str]] = None) -> FormattedPrompt:
        label = self._default_label
        _log.debug(s_("Retrieving Langfuse prompt template", template=name, label=label))
        prompt = self._fetch_prompt(name)
        config: Optional[PromptConfig] = None
        if prompt.config is not None:
            parsed: PromptConfig = parse_dict_pb(cast(dict, prompt.config), PromptConfig())
            if parsed.HasField("model"):
                config = parsed

        chat_prompt = prompt.compile(**params)
        system: Optional[str] = None
        user: Optional[str] = None
        for p in chat_prompt:
            if p.get("role") == "system":
                system = p.get("content")
            if p.get("role") == "user":
                user = p.get("content")
        return FormattedPrompt(
            system=SystemMessage(text=system),
            user=UserMessage(text=user),
            config=config,
            langfuse_prompt=prompt,
            prompt_name=prompt.name,
        )

    def _fetch_prompt(self, name: str) -> ChatPromptClient:
        label = self._default_label
        _log.debug(s_("Retrieving Langfuse prompt template", template=name, label=label))
        if label is not None:
            try:
                return self._langfuse.get_prompt(name=name, type="chat", label=label)
            except Exception as e:
                _log.debug(s_(
                    "Failed to get labeled prompt. Falling back to unlabeled", template=name, label=label, exc=e))
        return self._langfuse.get_prompt(name=name, type="chat")
