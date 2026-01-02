import subprocess
from typing import Optional

from dev_observer.repository.parser import parse_repository_url
from dev_observer.repository.provider import GitRepositoryProvider, RepositoryInfo
from dev_observer.repository.types import ObservedRepo


class DelegatingGitRepositoryProvider(GitRepositoryProvider):
    async def get_repo(self, repo: ObservedRepo) -> RepositoryInfo:
        parsed = parse_repository_url(repo.url, repo.git_repo.provider)
        return RepositoryInfo(
            owner=parsed.owner,
            name=parsed.name,
            clone_url=repo.url,
            # TODO: collect actual size.
            size_kb=500,
        )

    async def clone(self, repo: ObservedRepo, info: RepositoryInfo, dest: str, depth: Optional[str] = None):
        repo_root = _get_git_root()
        cmd = ["git", "clone"]
        if depth is not None:
            cmd.append(f"--depth={depth}")
        cmd.append(repo_root)
        cmd.append(dest)
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode != 0:
            raise RuntimeError(f"Failed to clone repository: {result.stderr}")

    async def get_authenticated_url(self, repo: ObservedRepo) -> str:
        return repo.url

    async def get_repo_token(self, repo: ObservedRepo) -> str:
        return ""


def _get_git_root() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True
    )
    return result.stdout.strip()
