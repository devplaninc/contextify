import os
import logging
from typing import List, Optional
import aiohttp
from gcloud.aio.storage import Storage

from dev_observer.api.types.observations_pb2 import Observation, ObservationKey
from dev_observer.observations.provider import ObservationsProvider


_log = logging.getLogger(__name__)


class GCSObservationsProvider(ObservationsProvider):
    _bucket: str
    """
    Implementation of ObservationsProvider that stores observations in Google Cloud Storage (GCS).
    Uses Application Default Credentials for authentication.
    """

    def __init__(self, bucket: str):
        self._bucket = bucket

    def _get_object_key(self, key: ObservationKey) -> str:
        return f"{key.kind}/{key.key}"

    async def exists(self, key: ObservationKey) -> bool:
        object_key = self._get_object_key(key)
        try:
            async with aiohttp.ClientSession() as session:
                client = Storage(session=session)
                # Try to get object metadata - if it exists, this will succeed
                await client.download(self._bucket, object_key, timeout=5)
            return True
        except aiohttp.ClientResponseError as e:
            if e.status == 404:
                return False
            else:
                error_msg = f"Error checking existence of observation {key.kind}/{key.name} in GCS: {str(e)}"
                _log.error(error_msg)
                raise RuntimeError(error_msg) from e
        except Exception as e:
            error_msg = f"Error checking existence of observation {key.kind}/{key.name} in GCS: {str(e)}"
            _log.error(error_msg)
            raise RuntimeError(error_msg) from e


    async def store(self, o: Observation):
        object_key = self._get_object_key(o.key)

        try:
            async with aiohttp.ClientSession() as session:
                client = Storage(session=session)
                # Convert content to bytes if it's a string
                content_bytes = o.content.encode('utf-8') if isinstance(o.content, str) else o.content
                await client.upload(
                    self._bucket,
                    object_key,
                    content_bytes
                )
            _log.debug(f"Stored observation {o.key.kind}/{o.key.key} in GCS")
        except aiohttp.ClientResponseError as e:
            error_msg = f"Error storing observation {o.key.kind}/{o.key.key} in GCS: {str(e)}"
            _log.error(error_msg)
            raise RuntimeError(error_msg) from e
        except Exception as e:
            error_msg = f"Error storing observation {o.key.kind}/{o.key.key} in GCS: {str(e)}"
            _log.error(error_msg)
            raise RuntimeError(error_msg) from e

    async def list(self, kind: str, path: Optional[str] = None) -> List[ObservationKey]:
        result: List[ObservationKey] = []
        # Build prefix - if path is specified, include it in the GCS prefix for efficiency
        prefix = f"{kind}/"
        if path is not None:
            prefix = f"{kind}/{path}"

        try:
            async with aiohttp.ClientSession() as session:
                client = Storage(session=session)
                # List all objects with the given prefix
                kind_prefix = f"{kind}/"

                # Use list_objects with prefix parameter
                response = await client.list_objects(self._bucket, params={'prefix': prefix})

                # Parse the response to extract object names
                items = response.get('items', [])
                for item in items:
                    full_key = item['name']
                    if full_key.startswith(kind_prefix):
                        key_part = full_key[len(kind_prefix):]
                        # Use the last part of the path as the name
                        name = os.path.basename(key_part)
                        result.append(ObservationKey(kind=kind, key=key_part, name=name))

                return result
        except aiohttp.ClientResponseError as e:
            error_msg = f"Error listing observations of kind '{kind}' from GCS: {str(e)}"
            _log.error(error_msg)
            raise RuntimeError(error_msg) from e
        except Exception as e:
            error_msg = f"Error listing observations of kind '{kind}' from GCS: {str(e)}"
            _log.error(error_msg)
            raise RuntimeError(error_msg) from e

    async def get(self, key: ObservationKey) -> Observation:
        """
        Get an observation from GCS.

        Args:
            key: The key of the observation to get

        Returns:
            The observation

        Raises:
            RuntimeError: If there's an error getting the observation
        """
        object_key = self._get_object_key(key)

        try:
            async with aiohttp.ClientSession() as session:
                client = Storage(session=session)
                content_bytes = await client.download(self._bucket, object_key)
                content = content_bytes.decode("utf-8")
                return Observation(key=key, content=content)
        except aiohttp.ClientResponseError as e:
            if e.status == 404:
                error_msg = f"Observation {key.kind}/{key.key} not found in GCS"
                _log.error(error_msg)
                raise RuntimeError(error_msg) from e
            error_msg = f"Error getting observation {key.kind}/{key.key} from GCS: {str(e)}"
            _log.error(error_msg)
            raise RuntimeError(error_msg) from e
        except Exception as e:
            error_msg = f"Error getting observation {key.kind}/{key.key} from GCS: {str(e)}"
            _log.error(error_msg)
            raise RuntimeError(error_msg) from e

    async def delete(self, key: ObservationKey) -> bool:
        object_key = self._get_object_key(key)

        try:
            async with aiohttp.ClientSession() as session:
                client = Storage(session=session)
                # Check if object exists first
                if not await self.exists(key):
                    return False

                await client.delete(self._bucket, object_key)
                _log.debug(f"Deleted observation {key.kind}/{key.key} from GCS")
                return True
        except aiohttp.ClientResponseError as e:
            error_msg = f"Error deleting observation {key.kind}/{key.key} from GCS: {str(e)}"
            _log.error(error_msg)
            raise RuntimeError(error_msg) from e
        except Exception as e:
            error_msg = f"Error deleting observation {key.kind}/{key.key} from GCS: {str(e)}"
            _log.error(error_msg)
            raise RuntimeError(error_msg) from e
