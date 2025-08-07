import logging

from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from dev_observer.api.types.repo_pb2 import RepoToken
from dev_observer.api.web.tokens_pb2 import (
    AddTokenRequest, AddTokenResponse, ListTokensResponse,
    GetTokenResponse, UpdateTokenRequest, UpdateTokenResponse, DeleteTokenResponse, ListTokensRequest
)
from dev_observer.log import s_
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import parse_dict_pb, Clock, RealClock, pb_to_dict

_log = logging.getLogger(__name__)


class TokensService:
    _store: StorageProvider
    _clock: Clock

    router: APIRouter

    def __init__(self, store: StorageProvider, clock: Clock = RealClock()):
        self._store = store
        self._clock = clock
        self.router = APIRouter()

        self.router.add_api_route("/tokens", self.add_token, methods=["POST"])
        self.router.add_api_route("/tokens/list", self.list_tokens, methods=["POST"])
        self.router.add_api_route("/tokens/token/{token_id}", self.get_token, methods=["GET"])
        self.router.add_api_route("/tokens/token/{token_id}", self.update_token, methods=["PUT"])
        self.router.add_api_route("/tokens/token/{token_id}", self.delete_token, methods=["DELETE"])

    async def add_token(self, req: Request):
        request = parse_dict_pb(await req.json(), AddTokenRequest())
        _log.debug(s_("Adding token", request=request))

        # Create RepoToken from request
        token = RepoToken(
            namespace=request.token.namespace,
            provider=request.token.provider,
            system=request.token.system,
            token=request.token.token,
            workspace=request.token.workspace,
            repo=request.token.repo,
        )
        if request.token.HasField("expires_at"):
            token.expires_at.FromDatetime(request.token.expires_at)

        saved_token = await self._store.add_token(token)
        return pb_to_dict(AddTokenResponse(token=saved_token))

    async def list_tokens(self, req: Request):
        request = parse_dict_pb(await req.json(), ListTokensRequest())
        _log.debug(s_("Listing tokens", request=request))

        tokens = await self._store.list_tokens(namespace=request.namespace)
        return pb_to_dict(ListTokensResponse(tokens=tokens))

    async def get_token(self, token_id: str):
        token = await self._store.get_token(token_id)
        if not token:
            raise HTTPException(status_code=404, detail="Token not found")
        return pb_to_dict(GetTokenResponse(token=token))

    async def update_token(self, token_id: str, req: Request):
        request = parse_dict_pb(await req.json(), UpdateTokenRequest())
        _log.debug(s_("Updating token", token_id=token_id, request=request))

        updated_token = await self._store.update_token(token_id, request.token)
        if not updated_token:
            raise HTTPException(status_code=404, detail="Token not found")
        return pb_to_dict(UpdateTokenResponse(token=updated_token))

    async def delete_token(self, token_id: str):
        _log.debug(s_("Deleting token", token_id=token_id))

        await self._store.delete_token(token_id)
        return pb_to_dict(DeleteTokenResponse())
