from github import Auth

from dev_observer.repository.types import ObservedRepo
from dev_observer.repository.github import GithubAuthProvider


class GithubTokenAuthProvider(GithubAuthProvider):
    _token: str

    def __init__(self, token: str):
        self._token = token

    async def get_auth(self, repo: ObservedRepo) -> Auth:
        return Auth.Token(self._token)

    async def get_cli_token_prefix(self, repo: ObservedRepo) -> str:
        return self._token

    async def get_token(self, repo: ObservedRepo) -> str:
        return self._token


