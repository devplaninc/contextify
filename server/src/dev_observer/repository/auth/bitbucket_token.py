import logging
from typing import Dict, Optional, List

from dev_observer.api.types.repo_pb2 import RepoToken
from dev_observer.common.schedule import pb_to_datetime
from dev_observer.log import s_
from dev_observer.repository.bitbucket import BitBucketAuthProvider
from dev_observer.repository.types import ObservedRepo
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import Clock, RealClock

_log = logging.getLogger(__name__)


class BitBucketTokenAuthProvider(BitBucketAuthProvider):
    _storage: StorageProvider
    _clock: Clock

    def __init__(self, storage: StorageProvider, clock: Clock = RealClock()):
        self._storage = storage
        self._clock = clock

    async def get_auth_headers(self, repo: ObservedRepo) -> Dict[str, str]:
        token = await self._get_best_token(repo)
        if not token:
            raise ValueError(f"No valid token found for repository {repo.git_repo.full_name}")
        return {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    async def get_cli_token_prefix(self, repo: ObservedRepo) -> str:
        """Get token prefix for git CLI operations."""
        token = await self._get_best_token(repo)
        if not token:
            raise ValueError(f"No valid token found for repository {repo.git_repo.full_name}")

        return f"x-token-auth:{token}"

    async def _get_best_token(self, repo: ObservedRepo) -> Optional[str]:
        full_name = repo.git_repo.full_name
        provider = repo.git_repo.provider

        # Extract workspace and repo info from full_name
        parts = full_name.split('/')
        if len(parts) != 2:
            raise ValueError(f"Invalid repository full name: {full_name}")

        workspace = parts[0]  # For BitBucket, this is the workspace; for GitHub, it's the owner
        repo_name = full_name  # Full repo name for repo-specific tokens

        # Get valid tokens in priority order
        tokens = await self._storage.find_tokens(
            provider=provider,
            workspace=workspace,
            repo=repo_name
        )
        _log.debug(s_("Found tokens", workspace=workspace, provider=provider, repo=repo_name, cnt=len(tokens)))
        tokens = self._get_valid_tokens(tokens)
        token = _best_token(tokens)

        if not token:
            _log.warning(f"No valid tokens found for {full_name} (provider: {provider})")
            return None

        return token.token


    def _get_valid_tokens(self, tokens: List[RepoToken]) -> List[RepoToken]:
        if not tokens:
            return []

        now = self._clock.now()
        result: List[RepoToken] = []
        for token in tokens:
            if token.HasField("expires_at") and pb_to_datetime(token.expires_at) < now:
                continue
            result.append(token)
        return result

def _best_token(tokens: List[RepoToken]) -> Optional[RepoToken]:
    if not tokens:
        return None
    def sort_key(token: RepoToken) -> int:
        if token.system:
            return 0
        elif token.workspace:
            return 1
        elif token.repo:
            return 2
        else:
            return 3
    sorted_tokens = sorted(tokens, key=sort_key)
    return sorted_tokens[0]




