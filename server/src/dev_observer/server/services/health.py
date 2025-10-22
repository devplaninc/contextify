import logging

from fastapi import APIRouter

from dev_observer.storage.provider import StorageProvider

_log = logging.getLogger(__name__)


class HealthService:
    _store: StorageProvider

    router: APIRouter

    def __init__(self, store: StorageProvider):
        self._store = store
        self.router = APIRouter()

        self.router.add_api_route("/live", self.live, methods=["GET"])

    async def live(self):
        await self._store.get_global_config()
        return {"status": "running", }
