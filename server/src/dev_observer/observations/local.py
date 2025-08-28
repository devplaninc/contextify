import os
from typing import List, Optional

from dev_observer.api.types.observations_pb2 import Observation, ObservationKey
from dev_observer.observations.provider import ObservationsProvider


class LocalObservationsProvider(ObservationsProvider):
    _dir: str

    def __init__(self, root_dir: str):
        self._dir = root_dir

    async def store(self, o: Observation):
        file_path = self._get_key_path(o.key)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as out_file:
            out_file.write(o.content)

    async def list(self, kind: str, path: Optional[str] = None) -> List[ObservationKey]:
        result: List[ObservationKey] = []
        kind_root = self._get_root(kind)
        for dirpath, _, files in os.walk(kind_root):
            for file in files:
                key = self._get_key(dirpath, file, kind_root)
                # If path is specified, only include keys that start with the specified path
                if path is not None and not key.startswith(path):
                    continue
                result.append(ObservationKey(kind=kind, key=key, name=file))

        return result

    async def get(self, key: ObservationKey) -> Observation:
        return Observation(key=key, content=self._read_content(key))

    async def exists(self, key: ObservationKey) -> bool:
        file_path = self._get_key_path(key)
        return os.path.exists(file_path)

    async def delete(self, key: ObservationKey) -> bool:
        file_path = self._get_key_path(key)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except OSError:
                return False
        return False

    def _get_root(self, kind: str) -> str:
        return os.path.join(self._dir, kind)

    def _get_key(self, dir_path: str, file: str, kind_root: str) -> str:
        path = os.path.join(dir_path, file)
        root_pref = f"{kind_root}/"
        return path[len(root_pref):] if path.startswith(root_pref) else path

    def _get_key_path(self, key: ObservationKey) -> str:
        return os.path.join(self._get_root(key.kind), key.key)

    def _read_content(self, key: ObservationKey) -> str:
        with open(self._get_key_path(key), 'r') as in_file:
            return in_file.read()
