import datetime
from typing import Optional

from dev_observer.api.types.repo_pb2 import GitRepository, GitMeta, GitAppInfo
from dev_observer.common.schedule import pb_to_datetime
from dev_observer.util import RealClock, Clock


def get_valid_repo_meta(repo: GitRepository, clock: Clock = RealClock()) -> Optional[GitMeta]:
    if repo.properties is None:
        return None
    if repo.properties.meta is None:
        return None
    last_refresh = repo.properties.meta.last_refresh
    if last_refresh is None:
        return None
    ts = pb_to_datetime(last_refresh)
    return repo.properties.meta if ts + datetime.timedelta(hours=3) > clock.now() else None


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
