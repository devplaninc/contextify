from abc import abstractmethod
from typing import Protocol, List, Optional

from dev_observer.api.types.observations_pb2 import Observation, ObservationKey


class ObservationsProvider(Protocol):
    @abstractmethod
    async def store(self, o: Observation):
        ...

    @abstractmethod
    async def list(self, kind: str, path: Optional[str] = None) -> List[ObservationKey]:
        ...

    @abstractmethod
    async def get(self, key: ObservationKey) -> Observation:
        ...

    @abstractmethod
    async def exists(self, key: ObservationKey) -> bool:
        ...
