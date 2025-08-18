import asyncio
import dataclasses
import logging
from typing import Literal, Optional, List, Dict, Any, TypedDict

from langchain_core.messages import AIMessage, ToolCall, BaseMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.constants import END
from langgraph.types import Command

from dev_observer.analysis.code.tools import bash_tools, bash_tool_names, execute_bash_command
from dev_observer.analysis.util import models
from dev_observer.analysis.util.models import extract_xml, chunk_messages, count_messages_tokens, \
    to_tool_result, clean_tools, to_str_content
from dev_observer.analysis.util.usage import extract_usage, sum_usage
from dev_observer.api.types.repo_pb2 import ResearchLog, ResearchLogItem, ToolCallResult
from dev_observer.log import s_
from dev_observer.prompts.provider import PromptsProvider, PrefixedPromptsFetcher, FormattedPrompt
from dev_observer.storage.provider import StorageProvider
from dev_observer.tokenizer.provider import TokenizerProvider
from dev_observer.util import Clock, RealClock, pb_to_dict

_log = logging.getLogger(__name__)


class AnalysisState(TypedDict, total=False):
    """
    Attributes:
        repo_path: The path to the checked-out repository that will be analyzed.
        max_iterations: The maximum number of iterations to be performed
            during the analysis process.
        general_prompt_prefix: Prefix for the general prompt to be used for analysis.
        task_prompt_prefix: Prefix for the task-specific prompt to be used for analysis.
    """
    repo_path: str
    max_iterations: int
    general_prompt_prefix: str
    task_prompt_prefix: str
    repo_url: str
    repo_name: str

    research_log: Optional[dict]
    full_analysis: Optional[str]
    analysis_summary: Optional[str]


@dataclasses.dataclass
class AnalysisResult:
    full: str
    summary: str
    response: BaseMessage

    chunk_responses: Optional[List[BaseMessage]] = None


@dataclasses.dataclass
class ResearchStep:
    iteration: int
    max_iterations: int
    repo_url: str
    repo_name: str
    history: List[BaseMessage]


@dataclasses.dataclass
class ResearchStepResult:
    log_item: ResearchLogItem
    stop: bool = False
    plan_response: Optional[BaseMessage] = None
    tool_messages: Optional[List[ToolMessage]] = None
    summarize_response: Optional[BaseMessage] = None


@dataclasses.dataclass
class ToolCallResponse:
    result: ToolCallResult
    tool_message: ToolMessage


@dataclasses.dataclass
class ChunkResponse:
    index: int
    response: BaseMessage


class CodeResearchNodes:
    _prompts: PrefixedPromptsFetcher
    _tokenizer: TokenizerProvider
    _storage: StorageProvider
    _clock: Clock

    def __init__(self,
                 prompts: PromptsProvider,
                 tokenizer: TokenizerProvider,
                 storage: StorageProvider,
                 clock: Clock = RealClock(),
                 ):
        self._prompts = PrefixedPromptsFetcher(prompts)
        self._tokenizer = tokenizer
        self._storage = storage
        self._clock = clock

    async def analyze_node(
            self, state: AnalysisState, config: RunnableConfig,
    ) -> Command[Literal["__end__"]]:
        p = {"op": "code_research", "node": "analyze", **_st(state)}
        messages: List[BaseMessage] = []
        try:
            global_config = await self._storage.get_global_config()
            max_tool_content = global_config.repo_analysis.research.max_tool_content_tokens
            iteration = 0
            max_iterations = state.get("max_iterations", 1)

            research_log = ResearchLog(
                started_at=self._clock.now(),
            )
            exit_reason = "max_iteration"
            _log.info(s_("Starting research", exit_reason=exit_reason, **p))
            while iteration < max_iterations:
                iteration += 1
                step = ResearchStep(
                    iteration=iteration,
                    max_iterations=max_iterations,
                    repo_url=state["repo_url"],
                    repo_name=state["repo_name"],
                    history=clean_tools(messages, self._tokenizer, 4, max_tool_content),
                )
                step_result = await self._do_research_iteration(state, config, step, max_tool_content)
                if step_result.plan_response:
                    messages.append(step_result.plan_response)
                if step_result.tool_messages:
                    messages.extend(step_result.tool_messages)
                if step_result.summarize_response:
                    messages.append(step_result.summarize_response)

                _log.debug(s_("Research step done", iteration=iteration, step_usage=step_result.log_item.usage, **p))

                research_log.total_usage.CopyFrom(sum_usage(research_log.total_usage, step_result.log_item.usage))

                research_log.items.append(step_result.log_item)
                if step_result.stop:
                    exit_reason = "done"
                    break
                if len(step_result.log_item.tool_calls) == 0:
                    _log.warning(s_("Unexpected research with no tool calls", **p))
                    continue
            _log.info(
                s_("Research finished, compiling report", total_usage=research_log.total_usage, exit_reason=exit_reason,
                   **p))

            step = ResearchStep(
                iteration=iteration,
                max_iterations=max_iterations,
                repo_url=state["repo_url"],
                repo_name=state["repo_name"],
                history=clean_tools(messages, self._tokenizer, -1, max_tool_content),
            )

            chunks_size = global_config.repo_analysis.research.report_chunk_size

            result = await self._produce_analysis(state, config, step, chunks_size)
            summary_usage = extract_usage(result.response)
            if result.chunk_responses:
                for resp in result.chunk_responses:
                    summary_usage = sum_usage(summary_usage, extract_usage(resp))
            research_log.total_usage.CopyFrom(sum_usage(research_log.total_usage, summary_usage))
            _log.info(s_("Research compiled", total_usage=research_log.total_usage, report_usage=summary_usage, **p))
            return Command(
                update={
                    "full_analysis": result.full,
                    "analysis_summary": result.summary,
                    "research_log": pb_to_dict(research_log),
                },
                goto=END,
            )
        except Exception as e:
            _log.exception(s_("Exception", error=str(e), **p))
            raise

    async def _do_research_iteration(
            self,
            state: AnalysisState,
            config: RunnableConfig,
            step: ResearchStep,
            max_tool_content: int,
    ) -> ResearchStepResult:
        p = {"op": "code_research", "node": "research_iteration", "iteration": step.iteration, **_st(state)}
        _log.debug(s_("Entering", **p))

        plan_response = await self._do_plan(state, config, step)
        log_item = ResearchLogItem(
            started_at=self._clock.now(),
            usage=extract_usage(plan_response)
        )
        plan_response.response_metadata["iteration"] = step.iteration
        step_result = ResearchStepResult(log_item=log_item)
        step_result.plan_response = plan_response

        has_tools = isinstance(plan_response, AIMessage) and len(plan_response.tool_calls) > 0
        if not has_tools:
            log_item.finished_at = self._clock.now()
            step_result.stop = True
            return step_result
        _log.debug(s_("Processing tools", **p))
        responses: List[ToolCallResponse] = await self._handle_tools(state, plan_response.tool_calls)
        tool_messages = [r.tool_message for r in responses]
        step_result.tool_messages = tool_messages
        for m in tool_messages:
            m.response_metadata["iteration"] = step.iteration

        log_item.tool_calls.extend([r.result for r in responses])

        sum_prompt = await self._get_prompt(state, step, "summarize")
        updated_history = [*step.history, plan_response, *tool_messages]
        sum_response = await models.ainvoke(config, sum_prompt, models.InvokeParams(
            history=clean_tools(updated_history, self._tokenizer, -1, max_tool_content),
        ), log_params=p)
        sum_response.response_metadata["iteration"] = step.iteration
        log_item.usage.CopyFrom(sum_usage(log_item.usage, extract_usage(sum_response)))

        _log.debug(s_("Summary response received", **p, response=sum_response))
        step_result.summarize_response = sum_response

        log_item.finished_at = self._clock.now()

        return step_result

    async def _do_plan(self, state: AnalysisState, config: RunnableConfig, step: ResearchStep, ) -> BaseMessage:
        p = {"op": "code_research", "node": "do_plan", "iteration": step.iteration, **_st(state)}
        plan_prompt = await self._get_prompt(state, step, "plan")
        invoke_params = models.InvokeParams(
            tools=bash_tools(),
            history=step.history,
        )
        plan_response = await models.ainvoke(config, plan_prompt, invoke_params, log_params=p)
        retry = 3
        while retry > 0:
            if plan_response.response_metadata.get('finish_reason', None) == 'MALFORMED_FUNCTION_CALL':
                _log.debug(s_("Got MALFORMED_FUNCTION_CALL", **p))
                await asyncio.sleep(1)
                retry -= 1
                _log.debug(s_("Retrying due to MALFORMED_FUNCTION_CALL", retries_left=retry, **p))
                plan_response = await models.ainvoke(config, plan_prompt, invoke_params, log_params=p)
            else:
                break
        _log.debug(s_("Plan response received", **p, response=plan_response))
        return plan_response

    async def _produce_analysis(
            self,
            state: AnalysisState,
            config: RunnableConfig,
            step: ResearchStep,
            chunk_threshold_tokens,
    ) -> AnalysisResult:
        p = {"op": "code_research", "node": "produce_analysis", "iteration": step.iteration, **_st(state)}
        # Check if history needs chunking
        total_tokens = count_messages_tokens(step.history, self._tokenizer)
        _log.debug(s_("History token count", total_tokens=total_tokens, **p))

        # no need to chunk if total size is under 1.5 chunk size
        if total_tokens <= 1.5*chunk_threshold_tokens:
            # Process normally if under token limit
            prompt = await self._get_prompt(state, step, "produce")
            response = await models.ainvoke(config, prompt, models.InvokeParams(history=step.history), log_params=p)
            _log.debug(s_("Analysis response received", **p, response=response))
            full = extract_xml(response.content, "full_analysis")
            if not full or len(full.strip()) < 50:
                # If the model didn't reply with a proper structured response, return the entire response as
                # a full report
                full = to_str_content(response.content)
            return AnalysisResult(
                full=full,
                summary=extract_xml(response.content, "analysis_summary"),
                response=response,
            )

        _log.info(s_("History exceeds token limit, chunking", total_tokens=total_tokens, **p))
        chunks = chunk_messages(step.history, self._tokenizer, chunk_threshold_tokens)
        chunk_responses: List[ChunkResponse] = await asyncio.gather(
            *[self._process_chunk(state, config, step, i, chunk) for i, chunk in enumerate(chunks)]
        )
        chunk_responses.sort(key=lambda x: x.index)

        # Combine all chunk results
        _log.debug(s_("Combining chunk analyses", num_chunks=len(chunks), **p))
        combined_step = ResearchStep(
            iteration=step.iteration,
            max_iterations=step.max_iterations,
            repo_url=step.repo_url,
            repo_name=step.repo_name,
            history=[]  # Empty history for combining step
        )

        chunk_summaries = "\n".join([f"## Chunk {i + 1} Analysis:\n{resp.response.content}\n"
                                     for i, resp in enumerate(chunk_responses)])

        combine_prompt = await self._get_prompt(state, combined_step, "produce-from-chunks",
                                                extra_params={"analsysis_chunks": chunk_summaries})

        final_response = await models.ainvoke(config, combine_prompt, models.InvokeParams(history=[]), log_params=p)

        _log.debug(s_("Final combined analysis received", **p, response=final_response))
        return AnalysisResult(
            full=extract_xml(final_response.content, "full_analysis"),
            summary=extract_xml(final_response.content, "analysis_summary"),
            response=final_response,
            chunk_responses=[r.response for r in chunk_responses],
        )

    async def _process_chunk(
            self,
            state: AnalysisState,
            config: RunnableConfig,
            step: ResearchStep,
            chunk_index: int,
            chunk: List[BaseMessage]) -> ChunkResponse:
        p = {"op": "code_research", "node": "process_chunk", "chunk_index": chunk_index, "iteration": step.iteration,
             **_st(state)}
        chunk_step = ResearchStep(
            iteration=step.iteration,
            max_iterations=step.max_iterations,
            repo_url=step.repo_url,
            repo_name=step.repo_name,
            history=chunk,
        )

        _log.debug(s_("Processing chunk", chunk_size=len(chunk), **p))
        chunk_prompt = await self._get_prompt(state, chunk_step, "produce-chunk")
        response = await models.ainvoke(config, chunk_prompt, models.InvokeParams(history=chunk), log_params=p)
        return ChunkResponse(index=chunk_index, response=response)

    async def _get_prompt(
            self, state: AnalysisState, step: ResearchStep, suffix: str, extra_params: Optional[dict] = None,
    ) -> FormattedPrompt:
        params = self._get_prompt_params(step)
        if extra_params:
            params.update(extra_params)
        general = await self._prompts.get(state["general_prompt_prefix"], suffix, params)
        task = await self._prompts.get(state["task_prompt_prefix"], "query", params)
        system = general.system
        if task.system and task.system.text:
            system.text = f"{system.text}\n\n{task.system.text}"
        return FormattedPrompt(
            config=task.config or general.config,
            system=system,
            user=task.user,
            langfuse_prompt=general.langfuse_prompt,
            prompt_name=general.prompt_name,
        )

    def _get_prompt_params(self, step: ResearchStep) -> Dict[str, str]:
        return {
            "iteration": step.iteration,
            "max_iterations": step.max_iterations,
            "repo_url": step.repo_url,
            "repo_name": step.repo_name,
        }

    async def _handle_tool(self, tool_call: ToolCall, repo_path: str) -> ToolCallResponse:
        p = {"op": "handle_tool", "tool_call": tool_call}
        _log.debug(s_("Entering", **p))
        allowed_tools = bash_tool_names()
        tool_name = tool_call["name"]
        response = ToolCallResponse(
            result=ToolCallResult(
                requested_tool_call=f"{tool_name}: {tool_call.get('args', {})}",
                status=ToolCallResult.ToolCallStatus.SUCCESS,
            ),
            tool_message=ToolMessage(
                tool_call_id=tool_call["id"],
                content="",
            ),
        )

        def set_msg(msg: str, success: bool = True):
            response.result.result = msg
            response.tool_message.content = msg
            if not success:
                response.result.status = ToolCallResult.ToolCallStatus.FAILURE
                response.tool_message.status = "error"

        try:
            _log.debug(s_("Entering", **p))
            if tool_name not in allowed_tools:
                set_msg(f"Unexpected tool: {tool_name}", False)
                return response
            tool_args = tool_call.get("args", {})
            command = tool_args.get("command", "")
            bash_result = await asyncio.wait_for(
                execute_bash_command(command, repo_path),
                timeout=45.0
            )
            set_msg(bash_result.result, bash_result.success)
            _log.debug(s_("Tool call finished", success=bash_result.success, **p))
            return response
        except asyncio.TimeoutError as e:
            set_msg(f"Tool {tool_name} timed out after", False)
            _log.exception(s_("Tool call timed out", exc=e, result=response.result.result, **p))
            return response
        except Exception as e:
            set_msg(f"Tool call failed: {e}", False)
            _log.exception(s_("Tool call timed out", exc=e, **p))
            return response

    async def _handle_tools(self, state: AnalysisState, tool_calls: List[ToolCall]) -> List[ToolCallResponse]:
        p: Dict[str, Any] = {"op": "code_research", "node": "handle_tools", **_st(state)}
        allowed_tools = bash_tool_names()
        bash_commands: List[str] = []
        _log.debug(s_("Entering", tool_calls=tool_calls, **p))
        responses: List[ToolCallResponse] = []
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            if tool_name not in allowed_tools:
                msg = ToolMessage(
                    tool_call_id=tool_call["id"],
                    content=f"Unexpected tool: {tool_name}",
                    status="error",
                )
                responses.append(ToolCallResponse(
                    tool_message=msg,
                    result=to_tool_result(tool_call, msg),
                ))
                continue
            tool_args = tool_call.get("args", {})
            bash_commands.append(tool_args.get("command", ""))
        call_results = await asyncio.gather(
            *[self._handle_tool(tool_call, state["repo_path"]) for tool_call in tool_calls],
        )
        _log.debug(s_("Tool calls done", **p))
        responses.extend(call_results)
        return responses


def _st(state: AnalysisState) -> dict:
    try:
        return {k: state.get(k) for k in ["max_iterations", "task_prompt_prefix", "repo_url"]}
    except BaseException as e:
        _log.exception(s_("Failed to get state params", error=e))
        return {}
