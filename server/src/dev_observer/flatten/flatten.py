import asyncio
import dataclasses
import logging
import os
import random
import shutil
import string
from datetime import datetime
from typing import List, Callable, Optional, Tuple
import shlex

from pydantic import BaseModel

from dev_observer.api.types.config_pb2 import GlobalConfig, RepoAnalysisConfig
from dev_observer.api.types.observations_pb2 import ObservationKey
from dev_observer.api.types.processing_pb2 import ProcessingItemResultData
from dev_observer.log import s_
from dev_observer.repository.cloner import clone_repository
from dev_observer.repository.provider import GitRepositoryProvider, RepositoryInfo
from dev_observer.repository.types import ObservedRepo, ObservedGitChanges
from dev_observer.tokenizer.provider import TokenizerProvider

_log = logging.getLogger(__name__)


@dataclasses.dataclass
class CombineResult:
    """Result of combining a repository into a single file."""
    file_path: str
    size_bytes: int
    output_dir: str


@dataclasses.dataclass
class FlattenResult:
    full_file_path: str
    """Result of breaking down a file into smaller files based on token count."""
    file_paths: List[str]
    total_tokens: int
    clean_up: Callable[[], bool]
    result_data: Optional[ProcessingItemResultData] = None


class RepomixInput(BaseModel):
    maxFileSize: int = 50_000_000


class RepomixGit(BaseModel):
    sortByChanges: bool = True
    sortByChangesMaxCommits: int = 100
    includeDiffs: bool = False


class RepomixOutput(BaseModel):
    filePath: str
    style: str = "markdown"
    parsableStyle: bool = False
    compress: bool = False
    # headerText: Optional[str] = None
    fileSummary: bool = True
    directoryStructure: bool = True
    files: bool = True
    removeComments: bool = False
    removeEmptyLines: bool = False
    topFilesLength: int = 5
    showLineNumbers: bool = False
    copyToClipboard: bool = False
    includeEmptyDirectories: bool = False
    git: RepomixGit = RepomixGit()


class RepomixIgnore(BaseModel):
    customPatterns: List[str] = []
    useGitignore: bool = True
    useDefaultPatterns: bool = True


class RepomixSecurity(BaseModel):
    enableSecurityCheck: bool = True


class RepomixTokenCount(BaseModel):
    encoding: str = "o200k_base"


class RepomixConfig(BaseModel):
    input: RepomixInput
    output: RepomixOutput
    include: List[str] = ["**/*"]
    ignore: RepomixIgnore = RepomixIgnore()
    security: RepomixSecurity = RepomixSecurity()
    tokenCount: RepomixTokenCount = RepomixTokenCount()


async def combine_repository(repo_path: str, info: RepositoryInfo, config: GlobalConfig) -> CombineResult:
    flatten_config = config.repo_analysis.flatten if config.repo_analysis.HasField("flatten") \
        else RepoAnalysisConfig.Flatten()
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    folder_path = os.path.join(repo_path, f"devplan_tmp_repomix_{suffix}")
    os.makedirs(folder_path)
    output_file = os.path.join(folder_path, "full.md")

    large_threshold_kb = (flatten_config.large_repo_threshold_mb or 500) * 1024
    is_large = info.size_kb > large_threshold_kb
    _log.info(s_("Starting repo flatten", is_large=is_large))

    compress = flatten_config.compress or (is_large and flatten_config.compress_large)
    ignore = flatten_config.ignore_pattern
    max_file_size = flatten_config.max_file_size_bytes or 50_000
    if is_large and len(flatten_config.large_repo_ignore_pattern) > 0:
        ignore = ",".join([ignore, flatten_config.large_repo_ignore_pattern])

    config = RepomixConfig(
        input=RepomixInput(maxFileSize=max_file_size),
        output=RepomixOutput(
            filePath=output_file,
            compress=compress,
            style=flatten_config.out_style if len(flatten_config.out_style) > 0 else "markdown",
        ),
        ignore=RepomixIgnore(customPatterns=[ignore]),
    )

    config_file = os.path.join(folder_path, "repomix.config.json")
    with open(config_file, 'w') as f:
        f.write(config.model_dump_json())

    # Run repomix to combine the repository into a single file
    cmd = f'repomix --config "{config_file}" "{repo_path}"'

    _log.debug(s_("Executing repomix...", output_file=output_file, cmd=cmd))
    out, err, code = await run_shell_command_async(cmd)

    if code != 0:
        _log.error(s_("Failed to repomix repository.", out=out, code=code))
        raise RuntimeError(f"Failed to combine repository: {err.decode('utf-8')}")

    _log.debug(s_("Done.", out=out.decode("utf-8"), output_file=output_file, ))

    # Clean up config file
    if os.path.exists(config_file):
        os.remove(config_file)

    # Get the size of the combined file
    size_bytes = os.path.getsize(output_file)

    return CombineResult(file_path=output_file, size_bytes=size_bytes, output_dir=folder_path)


@dataclasses.dataclass
class TokenizeResult:
    """Result of breaking down a file into smaller files based on token count."""
    file_paths: List[str]
    total_tokens: int


def tokenize_file(
        file_path: str,
        out_dir: str,
        tokenizer: TokenizerProvider,
        config: GlobalConfig,
) -> TokenizeResult:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    max_tokens_per_file = 100_000
    if config.repo_analysis.HasField("flatten"):
        max_tokens_per_file = config.repo_analysis.flatten.max_tokens_per_chunk
    if max_tokens_per_file <= 0:
        raise ValueError("max_tokens_per_file must be greater than 0")

    # Read the input file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Tokenize the content
    tokens = tokenizer.encode(content)
    total_tokens = len(tokens)
    if total_tokens <= max_tokens_per_file:
        return TokenizeResult(file_paths=[], total_tokens=total_tokens)

    # Create output files
    output_files = []
    for i in range(0, total_tokens, max_tokens_per_file):
        chunk_tokens = tokens[i:i + max_tokens_per_file]
        chunk_text = tokenizer.decode(chunk_tokens)
        out_file = os.path.join(out_dir, f"chunk_{i}.md")
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(chunk_text)

        output_files.append(out_file)

    return TokenizeResult(file_paths=output_files, total_tokens=total_tokens)


@dataclasses.dataclass
class FlattenRepoResult:
    flatten_result: FlattenResult
    repo: RepositoryInfo


async def flatten_repository(
        repo: ObservedRepo,
        provider: GitRepositoryProvider,
        tokenizer: TokenizerProvider,
        config: GlobalConfig,
) -> FlattenRepoResult:
    clone_result = await clone_repository(
        repo, provider,
        max_size_mb=config.repo_analysis.flatten.max_repo_size_mb,
        depth="1",
    )
    repo_path = clone_result.path
    combined_file_path: Optional[str] = None

    def clean_up():
        cleaned = False
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
            cleaned = True
        if clean_up is not None and os.path.exists(combined_file_path):
            os.remove(combined_file_path)
            cleaned = True
        return cleaned

    combine_result = await combine_repository(repo_path, clone_result.repo, config)
    combined_file_path = combine_result.file_path
    out_dir = combine_result.output_dir
    _log.debug(s_("Tokenizing..."))
    tokenize_result = tokenize_file(combined_file_path, out_dir, tokenizer, config)
    _log.debug(s_("File tokenized"))
    flatten_result = FlattenResult(
        full_file_path=combined_file_path,
        file_paths=tokenize_result.file_paths,
        total_tokens=tokenize_result.total_tokens,
        clean_up=clean_up,
    )
    return FlattenRepoResult(
        flatten_result=flatten_result,
        repo=clone_result.repo,
    )


async def flatten_repo_changes(
        params: ObservedGitChanges,
        provider: GitRepositoryProvider,
        tokenizer: TokenizerProvider,
        config: GlobalConfig,
) -> FlattenRepoResult:
    clone_result = await clone_repository(params.repo, provider)
    repo_path = clone_result.path
    combined_file_path: Optional[str] = None

    def clean_up():
        cleaned = False
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
            cleaned = True
        if clean_up is not None and os.path.exists(combined_file_path):
            os.remove(combined_file_path)
            cleaned = True
        return cleaned

    combine_result = await combine_commits(repo_path, params.from_date, params.to_date)
    combined_file_path = combine_result.file_path
    out_dir = combine_result.output_dir
    _log.debug(s_("Tokenizing...", combine_result=combine_result))
    tokenize_result = tokenize_file(combined_file_path, out_dir, tokenizer, config)
    _log.debug(s_("File tokenized", tokenize_result=tokenize_result))
    flatten_result = FlattenResult(
        full_file_path=combined_file_path,
        file_paths=tokenize_result.file_paths,
        total_tokens=tokenize_result.total_tokens,
        clean_up=clean_up,
    )
    return FlattenRepoResult(
        flatten_result=flatten_result,
        repo=clone_result.repo,
    )


async def combine_commits(repo_path: str, from_date: datetime, to_date: datetime) -> CombineResult:
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    folder_path = os.path.join(repo_path, f"devplan_tmp_commits_summary_{suffix}")
    os.makedirs(folder_path)
    output_file = os.path.join(folder_path, "full.txt")

    # Run repomix to combine the repository into a single file
    from_str = format_datetime_for_git(from_date)
    to_str = format_datetime_for_git(to_date)
    cmd = f'git log --pretty=format:"%h %an <%ae> %s" --since="{from_str}" --until="{to_str}" -p'
    _log.debug(s_("Executing git log...", output_file=output_file, cmd=cmd))
    out, err, code = await run_shell_command_async(cmd, cwd=repo_path)
    if code != 0:
        _log.error(s_("Failed to get log for repository.", out=out, code=code))
        raise RuntimeError(f"Failed to combine repository: {err}")

    with open(output_file, "w") as f:
        f.write(out.decode("utf-8"))

    _log.debug(s_("Done.", output_file=output_file))

    # Get the size of the combined file
    size_bytes = os.path.getsize(output_file)

    return CombineResult(file_path=output_file, size_bytes=size_bytes, output_dir=folder_path)


def format_datetime_for_git(dt: datetime) -> str:
    """Format datetime for git --since/--until parameters"""
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


async def run_shell_command_async(command: str, cwd: Optional[str] = None) -> Tuple[bytes, bytes, int]:
    process = await asyncio.create_subprocess_exec(
        *shlex.split(command),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd,
    )

    stdout, stderr = await process.communicate()
    return stdout, stderr, process.returncode
