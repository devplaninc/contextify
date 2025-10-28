import datetime
from typing import Optional, Tuple

from dev_observer.api.types.repo_pb2 import GitRepository, GitMeta, GitAppInfo, GitProperties, TokensInfo
from dev_observer.common.schedule import pb_to_datetime
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import RealClock, Clock


def get_valid_repo_meta(repo: GitRepository, clock: Clock = RealClock()) -> Tuple[Optional[GitMeta], bool]:
    if repo.properties is None:
        return None, True
    if repo.properties.meta is None:
        return None, True
    last_refresh = repo.properties.meta.last_refresh
    if last_refresh is None:
        return repo.properties.meta, True
    ts = pb_to_datetime(last_refresh)
    return repo.properties.meta, ts + datetime.timedelta(hours=3) <= clock.now()


def get_valid_repo_app_info(repo: GitRepository, clock: Clock = RealClock()) -> Optional[GitAppInfo]:
    if repo.properties is None:
        return None
    if repo.properties.app_info is None:
        return None
    last_refresh = repo.properties.app_info.last_refresh
    if last_refresh is None:
        return None
    ts = pb_to_datetime(last_refresh)
    return repo.properties.app_info if ts + datetime.timedelta(hours=3) > clock.now() else None
