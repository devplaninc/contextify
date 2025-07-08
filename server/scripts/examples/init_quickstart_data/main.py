import asyncio
import logging

from dev_observer.api.types.config_pb2 import RepoAnalysisConfig, AnalysisConfig, WebsiteCrawlingConfig
from dev_observer.api.types.observations_pb2 import Analyzer
from dev_observer.api.types.repo_pb2 import GitHubRepository
from dev_observer.log import s_
from dev_observer.server import detect

env = detect.env

_log = logging.getLogger(__name__)


async def init_global_config():
    config = await env.storage.get_global_config()
    if config.HasField("repo_analysis"):
        _log.info(s_("Global config already initialized", config=config))
        return
    config.repo_analysis.CopyFrom(RepoAnalysisConfig(
        flatten=RepoAnalysisConfig.Flatten(
            compress_large=True,
            large_repo_threshold_mb=5,
            max_repo_size_mb=150,
            large_repo_ignore_pattern="**/*.css",
            ignore_pattern="**/*.o,**/*.obj,**/*.exe,**/*.dll,**/*.so,**/*.dylib,**/*.a,**/*.class,**/*.jar,**/*.pyc,**/*.pyo,**/*.pyd,**/*.wasm,**/*.bin,**/*.lock,**/*.zip,**/*.tar,**/*.gz,**/*.rar,**/*.7z,**/*.egg,**/*.whl,**/*.deb,**/*.rpm,**/*.png,**/*.jpg,**/*.jpeg,**/*.gif,**/*.svg,**/*.ico,**/*.mp3,**/*.mp4,**/*.mov,**/*.webm,**/*.wav,**/*.ttf,**/*.woff,**/*.woff2,**/*.eot,**/*.otf,**/*.pdf,**/*.ai,**/*.psd,**/*.sketch,**/*.csv,**/*.tsv,**/*.json,**/*.xml,**/*.log,**/*.db,**/*.sqlite,**/*.h5,**/*.parquet,**/*.min.js,**/*.map,**/*.min.css,**/*.bundle.js,**/.DS_Store,**/*.swp,**/*.swo,**/*.iml,**/*.pb.go,**/*_pb2.py*,**/*.min.css,**/*.pem",
            out_style="markdown",
            remove_empty_lines=True,
            max_tokens_per_chunk=200_000,
            max_file_size_bytes=200_000,
        ),
        processing_interval_sec=15,
    ))
    config.analysis.CopyFrom(AnalysisConfig(
        repo_analyzers=[Analyzer(
            name="general",
            file_name="analysis.md",
            prompt_prefix="general-git",
        )],
        site_analyzers=[Analyzer(
            name="general",
            file_name="analysis.md",
            prompt_prefix="general-web",
        )],
        default_git_changes_analyzer=Analyzer(
            name="git-changes-default",
            file_name="git-changes-report.md",
            prompt_prefix="git-changes-default",
        )
    ))
    config.website_crawling.CopyFrom(WebsiteCrawlingConfig(
        website_scan_timeout_seconds=15,
        scrapy_response_timeout_seconds=5,
        crawl_depth=2,
        timeout_without_data_seconds=6,
    ))
    await env.storage.set_global_config(config)
    _log.info(s_("Global config initialized", config=config))


async def init_repositories():
    repos = await env.storage.get_github_repos()
    if len(repos) > 0:
        _log.info(s_("Repositories already initialized", repos=repos))
        return
    await env.storage.add_github_repo(GitHubRepository(
        name="dev-observer",
        full_name="devplaninc/dev-observer",
        url="https://github.com/devplaninc/dev-observer.git",
    ))

async def init_all():
    await asyncio.gather(
        init_global_config(),
        init_repositories(),
    )


if __name__ == "__main__":
    asyncio.run(init_all())