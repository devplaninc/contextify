import logging

from fastapi import APIRouter
from starlette.requests import Request

from dev_observer.api.types.processing_pb2 import ProcessingItemKey
from dev_observer.api.types.repo_pb2 import GitRepository
from dev_observer.api.web.repositories_pb2 import AddRepositoryRequest, AddRepositoryResponse, \
    ListRepositoriesResponse, RescanRepositoryResponse, GetRepositoryResponse, DeleteRepositoryResponse, \
    FilterRepositoriesRequest, FilterRepositoriesResponse
from dev_observer.log import s_
from dev_observer.repository.parser import parse_repository_url
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import parse_dict_pb, Clock, RealClock, pb_to_dict

_log = logging.getLogger(__name__)


class RepositoriesService:
    _store: StorageProvider
    _clock: Clock

    router: APIRouter

    def __init__(self, store: StorageProvider, clock: Clock = RealClock()):
        self._store = store
        self._clock = clock
        self.router = APIRouter()

        self.router.add_api_route("/repositories", self.add_repository, methods=["POST"])
        self.router.add_api_route("/repositories", self.list, methods=["GET"])
        self.router.add_api_route("/repositories/filter", self.filter, methods=["POST"])
        self.router.add_api_route("/repositories/{repo_id}", self.get, methods=["GET"])
        self.router.add_api_route("/repositories/{repo_id}", self.delete, methods=["DELETE"])
        self.router.add_api_route("/repositories/{repo_id}/rescan", self.rescan, methods=["POST"])

    async def add_repository(self, req: Request):
        request = parse_dict_pb(await req.json(), AddRepositoryRequest())
        _log.debug(s_("Adding repository", request=request))

        parsed_url = parse_repository_url(request.url, request.provider)
        repo = await self._store.add_git_repo(GitRepository(
            full_name=parsed_url.get_full_name(),
            name=parsed_url.name,
            url=request.url,
            provider=request.provider,
        ))

        return pb_to_dict(AddRepositoryResponse(repo=repo))

    async def get(self, repo_id: str):
        repo = await self._store.get_git_repo(repo_id)
        return pb_to_dict(GetRepositoryResponse(repo=repo))

    async def delete(self, repo_id: str):
        await self._store.delete_git_repo(repo_id)
        repos = await self._store.get_git_repos()
        return pb_to_dict(DeleteRepositoryResponse(repos=repos))

    async def list(self):
        repos = await self._store.get_git_repos()
        return pb_to_dict(ListRepositoriesResponse(repos=repos))

    async def filter(self, req: Request):
        request = parse_dict_pb(await req.json(), FilterRepositoriesRequest())
        repos = await self._store.filter_git_repos(request.filter)
        return pb_to_dict(FilterRepositoriesResponse(repos=repos))

    async def rescan(self, repo_id: str):
        await self._store.set_next_processing_time(
            ProcessingItemKey(github_repo_id=repo_id), self._clock.now(),
        )
        return pb_to_dict(RescanRepositoryResponse())
