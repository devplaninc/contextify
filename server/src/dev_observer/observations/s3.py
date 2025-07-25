import os
import logging
from typing import List
from botocore.exceptions import ClientError
from types_aiobotocore_s3 import S3Client

from dev_observer.api.types.observations_pb2 import Observation, ObservationKey
from dev_observer.observations.provider import ObservationsProvider
from aiobotocore.session import get_session


_log = logging.getLogger(__name__)


class S3ObservationsProvider(ObservationsProvider):
    _endpoint: str
    _bucket: str
    _access_key: str
    _secret_key: str
    _region: str
    """
    Implementation of ObservationsProvider that stores observations in an S3-compatible storage.
    """
    
    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket: str, region: str = "us-east-1"):
        self._endpoint = endpoint
        self._bucket = bucket
        self._access_key = access_key
        self._secret_key = secret_key
        self._region = region

    def _get_object_key(self, key: ObservationKey) -> str:
        return f"{key.kind}/{key.key}"

    async def exists(self, key: ObservationKey) -> bool:
        object_key = self._get_object_key(key)
        try:
            session = get_session()
            async with session.create_client(
                    's3',
                    region_name=self._region,
                    endpoint_url=self._endpoint,
                    aws_access_key_id=self._access_key,
                    aws_secret_access_key=self._secret_key,
            ) as client:
                client: S3Client
                await client.head_object(Bucket=self._bucket, Key=object_key)
            return True
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            if error_code == 'NoSuchKey':
                return False
            else:
                error_msg = f"Error checking existence of observation {key.kind}/{key.name} in S3: {str(e)}"
                _log.error(error_msg)
                raise RuntimeError(error_msg) from e


    async def store(self, o: Observation):
        """
        Store an observation in S3.
        
        Args:
            o: The observation to store
        
        Raises:
            RuntimeError: If there's an error storing the observation
        """
        object_key = self._get_object_key(o.key)
        
        try:
            session = get_session()
            async with session.create_client(
                    's3',
                    region_name=self._region,
                    endpoint_url=self._endpoint,
                    aws_access_key_id=self._access_key,
                    aws_secret_access_key=self._secret_key,
            ) as client:
                client: S3Client
                await client.put_object(
                    Bucket=self._bucket,
                    Key=object_key,
                    Body=o.content
                )
            _log.debug(f"Stored observation {o.key.kind}/{o.key.name} in S3")
        except ClientError as e:
            error_msg = f"Error storing observation {o.key.kind}/{o.key.name} in S3: {str(e)}"
            _log.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    async def list(self, kind: str) -> List[ObservationKey]:
        """
        List all observations of a specific kind.
        
        Args:
            kind: The kind of observations to list
            
        Returns:
            A list of ObservationKey objects
            
        Raises:
            RuntimeError: If there's an error listing the observations
        """
        result: List[ObservationKey] = []
        prefix = f"{kind}/"
        
        try:
            session = get_session()
            async with session.create_client(
                    's3',
                    region_name=self._region,
                    endpoint_url=self._endpoint,
                    aws_access_key_id=self._access_key,
                    aws_secret_access_key=self._secret_key,
            ) as client:
                client: S3Client
                # List all objects with the given prefix
                paginator = client.get_paginator('list_objects_v2')
                async for page in paginator.paginate(Bucket=self._bucket, Prefix=prefix):
                    for obj in page.get('Contents', []):
                        # Extract the key part after the kind prefix
                        full_key = obj['Key']
                        if full_key.startswith(prefix):
                            key_part = full_key[len(prefix):]
                            # Use the last part of the path as the name
                            name = os.path.basename(key_part)
                            result.append(ObservationKey(kind=kind, key=key_part, name=name))

                return result
        except ClientError as e:
            error_msg = f"Error listing observations of kind '{kind}' from S3: {str(e)}"
            _log.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    async def get(self, key: ObservationKey) -> Observation:
        """
        Get an observation from S3.
        
        Args:
            key: The key of the observation to get
            
        Returns:
            The observation
            
        Raises:
            RuntimeError: If there's an error getting the observation
        """
        object_key = self._get_object_key(key)
        
        try:
            session = get_session()
            async with session.create_client(
                    's3',
                    region_name=self._region,
                    endpoint_url=self._endpoint,
                    aws_access_key_id=self._access_key,
                    aws_secret_access_key=self._secret_key,
            ) as client:
                client: S3Client
                response = await client.get_object(Bucket=self._bucket, Key=object_key)
                body = await response['Body'].read()
                content = body.decode("utf-8")
                return Observation(key=key, content=content)
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            
            if error_code == 'NoSuchKey':
                error_msg = f"Observation {key.kind}/{key.name} not found in S3"
                _log.error(error_msg)
                raise RuntimeError(error_msg) from e
            else:
                error_msg = f"Error getting observation {key.kind}/{key.name} from S3: {str(e)}"
                _log.error(error_msg)
                raise RuntimeError(error_msg) from e