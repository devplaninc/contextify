import logging
from datetime import date
from typing import List

from dev_observer.analysis.provider import AnalysisProvider
from dev_observer.flatten.flatten import FlattenResult
from dev_observer.log import s_
from dev_observer.prompts.provider import PromptsProvider
from dev_observer.tokenizer.provider import TokenizerProvider

_log = logging.getLogger(__name__)

class TokenizedAnalyzer:
    prompts_prefix: str
    analysis: AnalysisProvider
    prompts: PromptsProvider
    summary_tokens_limit: int
    tokenizer: TokenizerProvider

    def __init__(
            self,
            prompts_prefix: str,
            analysis: AnalysisProvider,
            prompts: PromptsProvider,
            summary_tokens_limit: int,
            tokenizer: TokenizerProvider,
    ):
        self.prompts_prefix = prompts_prefix
        self.analysis = analysis
        self.prompts = prompts
        self.summary_tokens_limit = summary_tokens_limit
        self.tokenizer = tokenizer

    async def analyze_flatten(self, flatten_result: FlattenResult) -> str:
        session_id = f"{date.today().strftime("%Y-%m-%d")}.{flatten_result.full_file_path}"
        if len(flatten_result.file_paths) > 0:
            _log.debug(s_("Analyzing flatten (multiple)", files=flatten_result.file_paths))
            return await self._analyze_tokenized(
                flatten_result.file_paths, session_id)
        else:
            _log.debug(s_("Analyzing flatten (single)", file=flatten_result.full_file_path))
            return await self._analyze_file(
                flatten_result.full_file_path, f"{self.prompts_prefix}_analyze_full", session_id)

    async def _analyze_tokenized(self, paths: List[str], session_id: str) -> str:
        summaries: List[str] = []
        total_tokens = 0
        for p in paths:
            s = await self._analyze_file(p, f"{self.prompts_prefix}_analyze_chunk", session_id)
            tokens = len(self.tokenizer.encode(s))
            total_tokens += tokens
            if total_tokens > self.summary_tokens_limit:
                _log.warning(s_("Total summary exceeds limit, omitting some summaries",
                                total_tokens=total_tokens,
                                limit=self.summary_tokens_limit,
                                paths=paths
                                ))
                break
            summaries.append(s)

        summary = "\n\n-------\n\n".join(summaries)
        _log.info(s_("Analysing combined summaries",
                        total_tokens=total_tokens,
                        limit=self.summary_tokens_limit,
                        session_id=session_id,
                        paths_len=len(paths),
                        ))
        prompt = await self.prompts.get_formatted(f"{self.prompts_prefix}_analyze_combined_chunks", {
            "content": summary,
        })
        result = await self.analysis.analyze(prompt, session_id)
        return result.analysis

    async def _analyze_file(self, path: str, prompt_name: str, session_id: str) -> str:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        prompt = await self.prompts.get_formatted(prompt_name, {
            "content": content,
        })
        _log.debug(s_("Analyzing file", path=path, content_len=len(content)))
        result = await self.analysis.analyze(prompt, session_id)
        return result.analysis
