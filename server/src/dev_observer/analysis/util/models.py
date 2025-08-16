import base64
import dataclasses
import json
import logging
import os
import re
from typing import List, Optional, Union

import vertexai
from google.oauth2 import service_account
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

if (os.environ.get("INIT_VERTEX_AI", "false") == "true" and os.environ.get("GCP_PROJECT", None) is not None
        and os.environ.get("GCP_REGION", None) is not None):
    _credentials: Optional[service_account.Credentials] = None
    if os.environ.get("GOOGLE_SA_KEY", None) is not None:
        __sa_key = os.environ["GOOGLE_SA_KEY"]
        __decoded = base64.b64decode(__sa_key)
        _credentials = service_account.Credentials.from_service_account_info(json.loads(__decoded))

    _log.info(s_("Initializing Vertex AI client", creds_exist=_credentials is not None))

    vertexai.init(
        project=os.environ.get("GCP_PROJECT"),
        location=os.environ.get("GCP_REGION"),
        credentials=_credentials
    )
else:
    _log.info("Vertex AI init skipped")


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


def to_str_content(content: Union[str, list[Union[str, dict]]]) -> str:
    if isinstance(content, str):
        return content
    return '\n'.join(content)


def extract_xml(content: Union[str, list[Union[str, dict]]], tag: str) -> Optional[str]:
    text = to_str_content(content)
    match = re.search(f'<{tag}>(.*?)</{tag}>', text, re.DOTALL)
    return match.group(1) if match else None
