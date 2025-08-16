import asyncio
import dataclasses
import logging
from typing import Literal, Optional, List, Dict, Any

from langchain_core.messages import AIMessage, ToolCall, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.constants import END
from langgraph.graph import MessagesState
from langgraph.types import Command

from dev_observer.analysis.code.tools import bash_tools, bash_tool_names, execute_repo_bash_tool, _validate_bash_command, _execute_bash_pipeline
from dev_observer.analysis.util import models
from dev_observer.analysis.util.models import extract_xml
from dev_observer.log import s_
from dev_observer.prompts.provider import PromptsProvider, PrefixedPromptsFetcher

_log = logging.getLogger(__name__)


class AnalysisState(MessagesState, total=False):
    """
    Attributes:
        repo_path: The path to the checked-out repository that will be analyzed.
        max_iterations: The maximum number of iterations to be performed
            during the analysis process.
        prompt_prefix: Prefix for the prompt to be used for analysis.
    """
    repo_path: str
    max_iterations: int
    prompt_prefix: str

    iteration_count: Optional[int]
    full_analysis: Optional[str]
    analysis_summary: Optional[str]


@dataclasses.dataclass
class AnalysisResult:
    full: str
    summary: str


class CodeResearchNodes:
    _prompts: PrefixedPromptsFetcher

    def __init__(self, prompts: PromptsProvider):
        self._prompts = PrefixedPromptsFetcher(prompts)

    async def analyze_node(
            self, state: AnalysisState, config: RunnableConfig,
    ) -> Command[Literal["tools", "__end__"]]:
        p = {"op": "code_research", "node": "analyze", **_st(state)}
        try:
            _log.debug(s_("Entering", **p))

            async def produce() -> Command:
                result = await self._produce_analysis(state, config)
                return Command(
                    update={
                        "full_analysis": result.full,
                        "analysis_summary": result.summary,
                    },
                    goto=END,
                )

            if state.get("iteration_count", 0) >= state.get("max_iterations", 5):
                _log.debug(s_("Analysis done", reason="max_iterations", **p))
                return await produce()

            prompt = await self._prompts.get(state['prompt_prefix'], "analyze", self._get_prompt_params(state))
            response = await models.ainvoke(config, prompt, models.InvokeParams(
                tools=bash_tools(),
                history=state["messages"] or [],
            ))
            retry = 3
            while retry > 0:
                if response.response_metadata.get('finish_reason', None) == 'MALFORMED_FUNCTION_CALL':
                    await asyncio.sleep(20)
                    retry -= 1
                    _log.debug(s_("Retrying due to MALFORMED_FUNCTION_CALL", **p))
                    response = await models.ainvoke(config, prompt, models.InvokeParams(
                        tools=bash_tools(),
                        history=state["messages"] or [],
                    ))
                else:
                    break
            _log.debug(s_("Response received", response=response, **p))
            has_tools = isinstance(response, AIMessage) and len(response.tool_calls) > 0
            if not has_tools:
                _log.debug(s_("Analysis done", reason="no_tools", **p))
                return await produce()

            _log.debug(s_("Going to process tools", **p))
            return Command(
                update={"messages": [response], "iteration_count": state.get("iteration_count", 0) + 1},
                goto="tools",
            )
        except Exception as e:
            _log.exception(s_("Exception", error=str(e), **p))
            raise

    async def tools_node(self, state: AnalysisState) -> Command[Literal["analyze"]]:
        p: Dict[str, Any] = {"op": "code_research", "node": "tools", **_st(state)}
        try:
            repo_path = state["repo_path"]
            last_message = state["messages"][-1] if state["messages"] else None
            if not last_message:
                return Command(goto="analyze")
            tool_calls = last_message.tool_calls if isinstance(last_message, AIMessage) else []
            if not tool_calls or len(tool_calls) == 0:
                return Command(goto="analyze")

            tool_results: List[ToolMessage] = []
            allowed_tools = bash_tool_names()
            tools_to_call: List[ToolCall] = []
            for tool_call in last_message.tool_calls:
                tool_name = tool_call["name"]
                if tool_name not in allowed_tools:
                    tool_results.append(ToolMessage(
                        content=f"Unexpected tool: {tool_name}",
                        tool_call_id=tool_call["id"],
                        status="error",
                    ))
                    continue
                tools_to_call.append(tool_call)

            if len(tools_to_call) == 0:
                return Command(goto="analyze")

            p["tools"] = [f"{t["name"]} {t.get("args", "")}" for t in tools_to_call]
            _log.debug(s_("Calling tools", **p))

            task_results = await asyncio.gather(
                *[self._execute_bash_tool(repo_path, tool_call) for tool_call in tools_to_call],
                return_exceptions=True,
            )
            _log.debug(s_("Tool calls done", **p))
            tool_results.extend(task_results)

            return Command(
                update={"messages": tool_results},
                goto="analyze",
            )
        except BaseException as e:
            _log.exception(s_("Exception", error=str(e), **p))
            raise

    async def _execute_bash_tool(self, repo_path: str, tool_call: ToolCall, timeout: float = 45.0) -> ToolMessage:
        p = {"op": "code_research", "node": "tools_call", "repo_path": repo_path, "tool": tool_call["name"]}
        try:
            _log.debug(s_("Executing", **p))
            tool_args = tool_call.get("args", {})
            command = tool_args.get("command", "")
            result = await asyncio.wait_for(
                self._execute_bash_command(command, repo_path),
                timeout=timeout
            )

            _log.debug(s_("Executed", **p))
            return ToolMessage(
                content=result,
                tool_call_id=tool_call["id"]
            )
        except asyncio.TimeoutError:
            _log.error(s_("Tool execution timed out", timeout=timeout, **p))
            return ToolMessage(
                content=f"Tool {tool_call['name']} timed out after {timeout} seconds",
                tool_call_id=tool_call["id"],
                status="error",
            )
        except BaseException as e:
            _log.exception(s_("Failed", exc=e, **p))
            return ToolMessage(
                content=f"Error executing {tool_call["name"]}: {str(e)}",
                tool_call_id=tool_call["id"],
                status="error",
            )

    async def _execute_bash_command(self, command: str, repo_path: str) -> str:
        """Execute a bash command with validation and pipeline support."""
        if not _validate_bash_command(command):
            return "Error: Command contains disallowed commands or headless execution patterns"
        
        return await _execute_bash_pipeline(command, repo_path)

    async def _produce_analysis(self, state: AnalysisState, config: RunnableConfig) -> AnalysisResult:
        prompt = await self._prompts.get(state['prompt_prefix'], "produce", self._get_prompt_params(state))
        response = await models.ainvoke(config, prompt, models.InvokeParams(history=state["messages"] or []))
        content = response.content
        return AnalysisResult(
            full=extract_xml(content, "full_analysis"),
            summary=extract_xml(content, "analysis_summary"),
        )

    def _get_prompt_params(self, _: AnalysisState) -> Dict[str, str]:
        return {}


def _st(state: AnalysisState) -> dict:
    try:
        return {k: state.get(k) for k in ["iteration_count", "repo_path", "max_iterations", "prompt_prefix"]}
    except BaseException as e:
        _log.exception(s_("Failed to get state params", error=e))
        return {}
