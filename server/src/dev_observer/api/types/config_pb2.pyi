from dev_observer.api.types import observations_pb2 as _observations_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GlobalConfig(_message.Message):
    __slots__ = ("analysis", "repo_analysis", "website_crawling")
    ANALYSIS_FIELD_NUMBER: _ClassVar[int]
    REPO_ANALYSIS_FIELD_NUMBER: _ClassVar[int]
    WEBSITE_CRAWLING_FIELD_NUMBER: _ClassVar[int]
    analysis: AnalysisConfig
    repo_analysis: RepoAnalysisConfig
    website_crawling: WebsiteCrawlingConfig
    def __init__(self, analysis: _Optional[_Union[AnalysisConfig, _Mapping]] = ..., repo_analysis: _Optional[_Union[RepoAnalysisConfig, _Mapping]] = ..., website_crawling: _Optional[_Union[WebsiteCrawlingConfig, _Mapping]] = ...) -> None: ...

class AnalysisConfig(_message.Message):
    __slots__ = ("repo_analyzers", "site_analyzers", "disable_masking", "default_git_changes_analyzer", "default_aggregated_summary_analyzer", "code_research_analyzers")
    REPO_ANALYZERS_FIELD_NUMBER: _ClassVar[int]
    SITE_ANALYZERS_FIELD_NUMBER: _ClassVar[int]
    DISABLE_MASKING_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_GIT_CHANGES_ANALYZER_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_AGGREGATED_SUMMARY_ANALYZER_FIELD_NUMBER: _ClassVar[int]
    CODE_RESEARCH_ANALYZERS_FIELD_NUMBER: _ClassVar[int]
    repo_analyzers: _containers.RepeatedCompositeFieldContainer[_observations_pb2.Analyzer]
    site_analyzers: _containers.RepeatedCompositeFieldContainer[_observations_pb2.Analyzer]
    disable_masking: bool
    default_git_changes_analyzer: _observations_pb2.Analyzer
    default_aggregated_summary_analyzer: _observations_pb2.Analyzer
    code_research_analyzers: _containers.RepeatedCompositeFieldContainer[_observations_pb2.Analyzer]
    def __init__(self, repo_analyzers: _Optional[_Iterable[_Union[_observations_pb2.Analyzer, _Mapping]]] = ..., site_analyzers: _Optional[_Iterable[_Union[_observations_pb2.Analyzer, _Mapping]]] = ..., disable_masking: bool = ..., default_git_changes_analyzer: _Optional[_Union[_observations_pb2.Analyzer, _Mapping]] = ..., default_aggregated_summary_analyzer: _Optional[_Union[_observations_pb2.Analyzer, _Mapping]] = ..., code_research_analyzers: _Optional[_Iterable[_Union[_observations_pb2.Analyzer, _Mapping]]] = ...) -> None: ...

class UserManagementStatus(_message.Message):
    __slots__ = ("enabled", "public_api_key")
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_API_KEY_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    public_api_key: str
    def __init__(self, enabled: bool = ..., public_api_key: _Optional[str] = ...) -> None: ...

class RepoAnalysisConfig(_message.Message):
    __slots__ = ("flatten", "processing_interval_sec", "disabled", "research")
    class Flatten(_message.Message):
        __slots__ = ("compress", "remove_empty_lines", "out_style", "max_tokens_per_chunk", "max_repo_size_mb", "ignore_pattern", "large_repo_threshold_mb", "large_repo_ignore_pattern", "compress_large", "max_file_size_bytes")
        COMPRESS_FIELD_NUMBER: _ClassVar[int]
        REMOVE_EMPTY_LINES_FIELD_NUMBER: _ClassVar[int]
        OUT_STYLE_FIELD_NUMBER: _ClassVar[int]
        MAX_TOKENS_PER_CHUNK_FIELD_NUMBER: _ClassVar[int]
        MAX_REPO_SIZE_MB_FIELD_NUMBER: _ClassVar[int]
        IGNORE_PATTERN_FIELD_NUMBER: _ClassVar[int]
        LARGE_REPO_THRESHOLD_MB_FIELD_NUMBER: _ClassVar[int]
        LARGE_REPO_IGNORE_PATTERN_FIELD_NUMBER: _ClassVar[int]
        COMPRESS_LARGE_FIELD_NUMBER: _ClassVar[int]
        MAX_FILE_SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
        compress: bool
        remove_empty_lines: bool
        out_style: str
        max_tokens_per_chunk: int
        max_repo_size_mb: int
        ignore_pattern: str
        large_repo_threshold_mb: int
        large_repo_ignore_pattern: str
        compress_large: bool
        max_file_size_bytes: int
        def __init__(self, compress: bool = ..., remove_empty_lines: bool = ..., out_style: _Optional[str] = ..., max_tokens_per_chunk: _Optional[int] = ..., max_repo_size_mb: _Optional[int] = ..., ignore_pattern: _Optional[str] = ..., large_repo_threshold_mb: _Optional[int] = ..., large_repo_ignore_pattern: _Optional[str] = ..., compress_large: bool = ..., max_file_size_bytes: _Optional[int] = ...) -> None: ...
    class Research(_message.Message):
        __slots__ = ("max_repo_size_mb", "max_iterations")
        MAX_REPO_SIZE_MB_FIELD_NUMBER: _ClassVar[int]
        MAX_ITERATIONS_FIELD_NUMBER: _ClassVar[int]
        max_repo_size_mb: int
        max_iterations: int
        def __init__(self, max_repo_size_mb: _Optional[int] = ..., max_iterations: _Optional[int] = ...) -> None: ...
    FLATTEN_FIELD_NUMBER: _ClassVar[int]
    PROCESSING_INTERVAL_SEC_FIELD_NUMBER: _ClassVar[int]
    DISABLED_FIELD_NUMBER: _ClassVar[int]
    RESEARCH_FIELD_NUMBER: _ClassVar[int]
    flatten: RepoAnalysisConfig.Flatten
    processing_interval_sec: int
    disabled: bool
    research: RepoAnalysisConfig.Research
    def __init__(self, flatten: _Optional[_Union[RepoAnalysisConfig.Flatten, _Mapping]] = ..., processing_interval_sec: _Optional[int] = ..., disabled: bool = ..., research: _Optional[_Union[RepoAnalysisConfig.Research, _Mapping]] = ...) -> None: ...

class WebsiteCrawlingConfig(_message.Message):
    __slots__ = ("website_scan_timeout_seconds", "scrapy_response_timeout_seconds", "crawl_depth", "timeout_without_data_seconds")
    WEBSITE_SCAN_TIMEOUT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    SCRAPY_RESPONSE_TIMEOUT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    CRAWL_DEPTH_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_WITHOUT_DATA_SECONDS_FIELD_NUMBER: _ClassVar[int]
    website_scan_timeout_seconds: int
    scrapy_response_timeout_seconds: int
    crawl_depth: int
    timeout_without_data_seconds: int
    def __init__(self, website_scan_timeout_seconds: _Optional[int] = ..., scrapy_response_timeout_seconds: _Optional[int] = ..., crawl_depth: _Optional[int] = ..., timeout_without_data_seconds: _Optional[int] = ...) -> None: ...
