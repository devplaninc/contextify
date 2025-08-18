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
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolCall, ToolMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool

from dev_observer.analysis.util.usage import extract_usage
from dev_observer.api.types.ai_pb2 import ModelConfig
from dev_observer.api.types.repo_pb2 import ToolCallResult
from dev_observer.log import s_
from dev_observer.prompts.provider import FormattedPrompt
from dev_observer.tokenizer.provider import TokenizerProvider

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
        config: RunnableConfig,
        prompt: FormattedPrompt,
        params: Optional[InvokeParams] = None,
        *,
        log_params: Optional[dict] = None,
) -> BaseMessage:
    log_extra = {}
    if log_params is not None:
        log_extra.update(log_params)
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
        log_extra.update({"prompt_config": prompt.config, "prompt_name": prompt_name})
        _log.debug(s_("Creating prompt", **log_extra))
        pt = ChatPromptTemplate.from_messages(messages)
        if prompt.langfuse_prompt is not None:
            pt.metadata = {"langfuse_prompt": prompt.langfuse_prompt}
        pv = await pt.ainvoke(params.input, config=config)
        _log.debug(s_("Invoking model", **log_extra))
        response = await model.ainvoke(pv, config=config)
        _log.debug(s_("Model replied", usage=extract_usage(response), **log_extra))
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


def count_message_tokens(msg: BaseMessage, tokenizer: TokenizerProvider) -> int:
    return len(tokenizer.encode(msg.content))


def count_messages_tokens(messages: List[BaseMessage], tokenizer: TokenizerProvider) -> int:
    """Count total tokens in a list of messages."""
    total_tokens = 0
    for message in messages:
        total_tokens += count_message_tokens(message, tokenizer)
    return total_tokens


def chunk_messages(
        messages: List[BaseMessage],
        tokenizer: TokenizerProvider,
        max_tokens: int = 200000,
        boundary_tag: str = "iteration",
) -> List[List[BaseMessage]]:
    """Chunk messages into groups, splitting when token limit is exceeded but only at tag boundaries."""
    if not messages:
        return []
    chunks = []
    current_chunk = []
    current_tokens = 0
    current_tag = None
    needs_split = False  # Flag to track when we need to split at next tag boundary

    for message in messages:
        message_tokens = count_message_tokens(message, tokenizer)
        message_tag = message.response_metadata.get(boundary_tag, None)
        at_boundary = current_tag is not None and message_tag != current_tag

        # Check if adding this message would exceed the token limit
        would_exceed_limit = current_chunk and current_tokens + message_tokens > max_tokens

        if at_boundary and (needs_split or would_exceed_limit):
            # Split at tag boundary when we need to or would exceed limit
            chunks.append(current_chunk)
            current_chunk = [message]
            current_tokens = message_tokens
            current_tag = message_tag
            needs_split = False
            _log.debug(s_("Split chunk at tag boundary",
                          previous_tag=current_tag,
                          new_tag=message_tag,
                          chunk_tokens=current_tokens))
        elif would_exceed_limit and not at_boundary:
            # Mark that we need to split at the next tag boundary
            needs_split = True
            current_chunk.append(message)
            current_tokens += message_tokens
            _log.debug(s_("Token limit exceeded, will split at next tag boundary",
                          current_tag=current_tag,
                          message_tag=message_tag,
                          current_tokens=current_tokens,
                          max_tokens=max_tokens))
            current_tag = message_tag
        else:
            # Add message to current chunk
            current_chunk.append(message)
            current_tokens += message_tokens
            current_tag = message_tag

    # Add the last chunk if it has messages
    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def to_tool_result(tool_call: ToolCall, tool_msg: ToolMessage) -> ToolCallResult:
    tool_name = tool_call["name"]
    status = ToolCallResult.ToolCallStatus.SUCCESS if tool_msg.status == "success" \
        else ToolCallResult.ToolCallStatus.FAILURE
    return ToolCallResult(
        requested_tool_call=f"{tool_name}: {tool_call.get('args', {})}",
        result=tool_msg.content,
        status=status,
    )


def clean_tools(
        messages: List[BaseMessage],
        tokenizer: TokenizerProvider,
        depth: int = 0,
        max_tool_tokens: Optional[int] = None,
) -> List[BaseMessage]:
    """
    Create a new copy of messages where ToolMessage "content" is truncated if larger than max_tool_tokens.

    Args:
        messages: List of messages to clean
        tokenizer: Tokenizer to use for counting tokens
        depth: Only clean ToolMessages before the latest AIMessage at the specified depth. If -1, do not clean,
        but still truncate every message.
        max_tool_tokens: Maximum number of tokens to keep in tool results

    Returns:
        New list of messages with ToolMessage content truncated when necessary
    """

    if not messages:
        return []

    if max_tool_tokens <= 0:
        max_tool_tokens = None

    result = []

    if depth < 0:
        # Do not clean but truncate every message
        for msg in messages:
            if isinstance(msg, ToolMessage):
                result.append(truncate_tool_msg(msg, tokenizer, max_tool_tokens))
            else:
                result.append(msg)
        return result

    if depth == 0:
        for msg in messages:
            if isinstance(msg, ToolMessage):
                result.append(clean_tool_msg(msg))
            else:
                result.append(msg)
        return result

    # Find the latest AIMessage at the specified depth
    ai_message_indices = []
    for i, msg in enumerate(messages):
        if isinstance(msg, AIMessage):
            ai_message_indices.append(i)

    # If we don't have enough AIMessages for the specified depth, clean nothing
    if len(ai_message_indices) < depth:
        return messages[:]  # Return a shallow copy

    # Get the index of the latest AIMessage at the specified depth
    # depth=1 means the latest AIMessage, depth=2 means the second-to-latest, etc.
    latest_ai_index = ai_message_indices[-depth]

    # Clean ToolMessages only before this AIMessage
    for i, msg in enumerate(messages):
        if isinstance(msg, ToolMessage):
            if i < latest_ai_index:
                result.append(clean_tool_msg(msg))
            else:
                result.append(truncate_tool_msg(msg, tokenizer, max_tool_tokens))
        else:
            result.append(msg)

    return result


def truncate_tool_msg(
        msg: ToolMessage,
        tokenizer: TokenizerProvider,
        max_tool_tokens: Optional[int] = None,
) -> ToolMessage:
    if max_tool_tokens is None:
        return msg
    str_content = to_str_content(msg.content)
    token_count = len(tokenizer.encode(str_content))

    # adding a small buffer to avoid cutting just a couple chars
    if token_count > (max_tool_tokens + 500):
        # Encode and truncate to max_tool_tokens, then decode back to text
        tokens = tokenizer.encode(str_content)
        truncated_tokens = tokens[:max_tool_tokens]
        truncated_content = tokenizer.decode(truncated_tokens)
        final_content = truncated_content + " [REDACTED: CONTENT TOO LONG]"
        return ToolMessage(content=final_content, tool_call_id=msg.tool_call_id, status=msg.status)

    # Always return with string content, even if under limit
    return ToolMessage(content=str_content, tool_call_id=msg.tool_call_id, status=msg.status)


def clean_tool_msg(msg: ToolMessage, threshold: int = 0) -> ToolMessage:
    str_content = to_str_content(msg.content)
    if len(str_content) > threshold:
        return ToolMessage(content="[REDACTED]", tool_call_id=msg.tool_call_id, status=msg.status)
    return msg
