from typing import List, Optional

from dev_observer.api.types.observations_pb2 import ObservationKey, Observation
from dev_observer.observations.provider import ObservationsProvider


class MemoryObservationsProvider(ObservationsProvider):
    def __init__(self):
        self._observations: List[Observation] = []

    async def store(self, o: Observation):
        self._observations.append(o)

    async def list(self, kind: str, path: Optional[str] = None) -> List[ObservationKey]:
        result = []
        for o in self._observations:
            # Filter by kind
            if o.key.kind != kind:
                continue
            # If path is specified, only include keys that start with the specified path
            if path is not None and not o.key.key.startswith(path):
                continue
            result.append(o.key)
        return result

    async def get(self, key: ObservationKey) -> Observation:
        for o in self._observations:
            if o.key == key:
                return o
        raise ValueError(f"Observation {key} not found")

    async def exists(self, key: ObservationKey) -> bool:
        for o in self._observations:
            if o.key == key:
                return True
        return False