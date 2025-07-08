import logging
from abc import abstractmethod
from typing import Protocol, Dict, Any, Optional
from datetime import datetime

from dev_observer.log import s_
from dev_observer.util import Clock, RealClock

_log = logging.getLogger(__name__)


class AnalyticsProvider(Protocol):
    @abstractmethod
    async def track_event(self, event_name: str, properties: Dict[str, Any], user_id: Optional[str] = None):
        ...

    @abstractmethod
    async def track_error(self, error_name: str, error_message: str, properties: Dict[str, Any], user_id: Optional[str] = None):
        ...


class LoggingAnalyticsProvider(AnalyticsProvider):
    """Simple analytics provider that logs events"""
    
    def __init__(self, clock: Clock = RealClock()):
        self._clock = clock

    async def track_event(self, event_name: str, properties: Dict[str, Any], user_id: Optional[str] = None):
        _log.info(s_("Analytics Event", 
                    event=event_name,
                    user_id=user_id,
                    properties=properties,
                    timestamp=self._clock.now().isoformat()))

    async def track_error(self, error_name: str, error_message: str, properties: Dict[str, Any], user_id: Optional[str] = None):
        _log.error(s_("Analytics Error",
                     error=error_name,
                     message=error_message,
                     user_id=user_id,
                     properties=properties,
                     timestamp=self._clock.now().isoformat()))


class ChangeAnalysisAnalytics:
    """Analytics wrapper for change analysis events"""
    
    def __init__(self, provider: AnalyticsProvider):
        self._provider = provider

    async def track_enrollment(self, repo_id: str, repo_name: str, user_id: Optional[str] = None):
        await self._provider.track_event("repo_change_analysis_enrolled", {
            "repo_id": repo_id,
            "repo_name": repo_name
        }, user_id)

    async def track_unenrollment(self, repo_id: str, repo_name: str, user_id: Optional[str] = None):
        await self._provider.track_event("repo_change_analysis_unenrolled", {
            "repo_id": repo_id,
            "repo_name": repo_name
        }, user_id)

    async def track_analysis_started(self, repo_id: str, repo_name: str, analysis_id: str):
        await self._provider.track_event("repo_change_analysis_started", {
            "repo_id": repo_id,
            "repo_name": repo_name,
            "analysis_id": analysis_id
        })

    async def track_analysis_completed(self, repo_id: str, repo_name: str, analysis_id: str, 
                                     commits_count: int, prs_count: int, summary_length: int):
        await self._provider.track_event("repo_change_analysis_completed", {
            "repo_id": repo_id,
            "repo_name": repo_name,
            "analysis_id": analysis_id,
            "commits_count": commits_count,
            "prs_count": prs_count,
            "summary_length": summary_length
        })

    async def track_analysis_failed(self, repo_id: str, repo_name: str, analysis_id: str, 
                                  error_message: str, error_type: str):
        await self._provider.track_error("repo_change_analysis_failed", error_message, {
            "repo_id": repo_id,
            "repo_name": repo_name,
            "analysis_id": analysis_id,
            "error_type": error_type
        })

    async def track_summary_access(self, repo_id: str, repo_name: str, analysis_id: str, user_id: Optional[str] = None):
        await self._provider.track_event("repo_change_analysis_summary_accessed", {
            "repo_id": repo_id,
            "repo_name": repo_name,
            "analysis_id": analysis_id
        }, user_id)

    async def track_api_access(self, endpoint: str, repo_id: str, user_id: Optional[str] = None, 
                             filters: Optional[Dict[str, Any]] = None):
        await self._provider.track_event("repo_change_analysis_api_access", {
            "endpoint": endpoint,
            "repo_id": repo_id,
            "filters": filters or {}
        }, user_id)