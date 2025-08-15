import dataclasses
import logging
import re
from typing import List, Optional, Union

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool

from dev_observer.api.types.ai_pb2 import ModelConfig
from dev_observer.log import s_
from dev_observer.prompts.provider import FormattedPrompt

_log = logging.getLogger(__name__)


def model_from_config(config: ModelConfig) -> BaseChatModel:
    return init_chat_model(f"{config.provider}:{config.model_name}")


def extract_prompt_messages(prompt: FormattedPrompt) -> List[BaseMessage]:
    messages: List[BaseMessage] = []
    if prompt.system is not None:
        messages.append(SystemMessage(content=prompt.system.text))
    if prompt.user is not None:
        contents: List[Union[str, dict]] = []
        text = prompt.user.text
        if text is not None and len(text) > 0:
            contents.append({"type": "text", "text": text})
        for image_url in prompt.user.image_urls:
            if image_url is None or len(image_url) == 0:
                contents.append({"type": "image_url", "image_url": {"url": image_url}})
        messages.append(HumanMessage(content=contents))
    return messages


@dataclasses.dataclass
class InvokeParams:
    input: dict = dataclasses.field(default_factory=dict)
    tools: Optional[List[BaseTool]] = None
    history: List[BaseMessage] = dataclasses.field(default_factory=list)


async def ainvoke(
        config: RunnableConfig, prompt: FormattedPrompt, params: Optional[InvokeParams] = None,
) -> BaseMessage:
    log_extra = {}
    try:
        if params is None:
            params = InvokeParams()

        prompt_config = prompt.config
        if prompt_config is None or prompt_config.model is None:
            raise ValueError("Missing model in prompt config")
        model = model_from_config(prompt_config.model)
        if params.tools is not None:
            model = model.bind_tools(params.tools)
        prompt_name = prompt.prompt_name
        messages = extract_prompt_messages(prompt)
        messages = [*messages, *params.history]
        log_extra = {"prompt_config": prompt.config, "prompt_name": prompt_name}
        _log.debug(s_("Creating prompt", **log_extra))
        pt = ChatPromptTemplate.from_messages(messages)
        if prompt.langfuse_prompt is not None:
            pt.metadata = {"langfuse_prompt": prompt.langfuse_prompt}
        pv = await pt.ainvoke(params.input, config=config)
        _log.debug(s_("Invoking model", **log_extra))
        response = await model.ainvoke(pv, config=config)
        _log.debug(s_("Model replied", **log_extra))
        return response
    except BaseException as e:
        _log.exception(s_("Model failed", error=e, **log_extra))
        raise


def extract_xml(text: str, tag: str) -> str:
    """
    Extracts the content of the specified XML tag from the given text. Used for parsing structured responses

    Args:
        text (str): The text containing the XML.
        tag (str): The XML tag to extract content from.

    Returns:
        str: The content of the specified XML tag, or an empty string if the tag is not found.
    """
    match = re.search(f'<{tag}>(.*?)</{tag}>', text, re.DOTALL)
    return match.group(1) if match else ""
