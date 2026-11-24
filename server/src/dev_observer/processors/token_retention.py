import asyncio
import logging

from dev_observer.log import s_
from dev_observer.storage.provider import StorageProvider

_log = logging.getLogger(__name__)


class TokenRetentionMaintenance:
    """Run one bounded sweep at startup, then at most once per 15 minutes."""

    def __init__(self, storage: StorageProvider, interval_seconds: float = 900):
        self._storage = storage
        self._interval_seconds = interval_seconds
        self._next_run = 0.0

    async def run_if_due(self):
        now = asyncio.get_running_loop().time()
        if now < self._next_run:
            return
        # Advance before attempting cleanup so failures don't retry every tick.
        self._next_run = now + self._interval_seconds
        try:
            cleanup = getattr(self._storage, "cleanup_expired_forge_tokens", None)
            if cleanup is None:
                return
            # Bound the total delay to normal background polling, including DB waits.
            async with asyncio.timeout(10):
                deleted = await cleanup()
            if deleted:
                _log.info(s_("Pruned expired Forge system tokens", deleted=deleted))
        except Exception:
            _log.exception("Forge token retention sweep failed; retrying next interval")
