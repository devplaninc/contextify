import logging
from datetime import datetime

from github import Auth, GithubIntegration

from dev_observer.api.types.repo_pb2 import GitAppInfo, GitProperties
from dev_observer.repository.types import ObservedRepo
from dev_observer.repository.github import GithubAuthProvider
from dev_observer.repository.util import get_valid_repo_app_info
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import Clock, RealClock

_log = logging.getLogger(__name__)


class GithubAppAuthProvider(GithubAuthProvider):
    _private_key: str
    _app_id: str
    _storage: StorageProvider
    _clock: Clock

    def __init__(self, app_id: str, private_key: str, storage: StorageProvider, clock: Clock = RealClock()):
        self._private_key = private_key
        self._app_id = app_id
        self._storage = storage
        self._clock = clock

    async def get_auth(self, repo: ObservedRepo) -> Auth:
        auth = Auth.AppAuth(self._app_id, self._private_key)
        installation_id = await self._get_installation_id(auth, repo)
        return auth.get_installation_auth(installation_id)

    async def get_cli_token_prefix(self, repo: ObservedRepo) -> str:
        auth = Auth.AppAuth(self._app_id, self._private_key)
        installation_id = await self._get_installation_id(auth, repo)
        with GithubIntegration(auth=auth) as gh:
            token = gh.get_access_token(installation_id).token
            return f"x-access-token:{token}"

    async def _get_installation_id(self, auth: Auth.AppAuth, repo: ObservedRepo) -> int:
        full_name = repo.git_repo.full_name
        parts = full_name.split("/")
        if len(parts) != 2:
            raise ValueError(f"Invalid repository name [{full_name}]")
        app_info = get_valid_repo_app_info(repo.git_repo)
        if app_info is not None:
            return app_info.installation_id

        with GithubIntegration(auth=auth) as gh:
            installation_id = gh.get_repo_installation(parts[0], parts[1]).id
            app_info = GitAppInfo(
                last_refresh=self._clock.now(),
                installation_id=installation_id
            )
        stored_repo = repo.git_repo
        if not stored_repo.HasField("properties"):
            stored_repo.properties.CopyFrom(GitProperties())
        stored_repo.properties.app_info.CopyFrom(app_info)
        repo.git_repo = await self._storage.update_repo_properties(stored_repo.id, stored_repo.properties)
        return app_info.installation_id
