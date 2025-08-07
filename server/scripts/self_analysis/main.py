import asyncio
import logging
import os
import subprocess

from dotenv import load_dotenv

import dev_observer.log
from dev_observer.api.types.config_pb2 import GlobalConfig
from dev_observer.api.types.observations_pb2 import ObservationKey
from dev_observer.api.types.repo_pb2 import GitRepository, GitProvider
from dev_observer.env_detection import detect_server_env
from dev_observer.processors.flattening import ObservationRequest
from dev_observer.repository.types import ObservedRepo
from dev_observer.settings import Settings

dev_observer.log.encoder = dev_observer.log.PlainTextEncoder()
logging.basicConfig(level=logging.DEBUG)
_log = logging.getLogger(__name__)

_repo = "git@github.com:devplaninc/dev-observer.git"

_offline = False


def get_git_root() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True
    )
    return result.stdout.strip()


async def main():
    repo_root = get_git_root()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(repo_root, "server", ".env"))
    load_dotenv(os.path.join(repo_root, "server", ".env.local"))

    os.environ["DEV_OBSERVER__PROMPTS__LOCAL__DIR"] = os.path.join(current_dir, "prompts")
    os.environ["DEV_OBSERVER__OBSERVATIONS__LOCAL__DIR"] = os.path.join(repo_root, "_local_data")
    if _offline:
        os.environ["DEV_OBSERVER__GIT__PROVIDER"] = "copying"
        os.environ["DEV_OBSERVER__ANALYSIS__PROVIDER"] = "stub"
        os.environ["DEV_OBSERVER__TOKENIZER__PROVIDER"] = "stub"
    Settings.model_config["toml_file"] = os.path.join(current_dir, "config.toml")
    env = detect_server_env(Settings())
    await env.repos_processor.process(ObservedRepo(url=_repo, git_repo=GitRepository(provider=GitProvider.GITHUB)), [
        ObservationRequest(
            prompt_prefix="self",
            key=ObservationKey(kind="repos", name="analysis.md", key="devplaninc/dev-observer/analysis.md"),
        )
    ], GlobalConfig())


if __name__ == "__main__":
    asyncio.run(main())
