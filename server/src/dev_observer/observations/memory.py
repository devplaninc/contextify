from typing import List

from dev_observer.api.types.observations_pb2 import ObservationKey, Observation
from dev_observer.observations.provider import ObservationsProvider


class MemoryObservationsProvider(ObservationsProvider):
    _observations: List[Observation] = []

    async def store(self, o: Observation):
        self._observations.append(o)

    async def list(self, kind: str) -> List[ObservationKey]:
        return [o.key for o in self._observations]

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