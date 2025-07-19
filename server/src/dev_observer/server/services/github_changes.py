import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException

from dev_observer.api.types.observations_pb2 import ObservationKey
from dev_observer.log import s_
from dev_observer.observations.provider import ObservationsProvider
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import Clock, RealClock

_log = logging.getLogger(__name__)


class GitHubChangesService:
    """Service for accessing GitHub repository changes summaries."""
    
    _observations: ObservationsProvider
    _storage: StorageProvider
    _clock: Clock
    router: APIRouter

    def __init__(
        self, 
        observations: ObservationsProvider, 
        storage: StorageProvider,
        clock: Clock = RealClock()
    ):
        self._observations = observations
        self._storage = storage
        self._clock = clock
        self.router = APIRouter()

        # Add API routes
        self.router.add_api_route("/github-changes", self.list_all_changes, methods=["GET"])
        self.router.add_api_route("/github-changes/{repo_id}", self.get_repo_changes, methods=["GET"])
        self.router.add_api_route("/github-changes/{repo_id}/trigger", self.trigger_analysis, methods=["POST"])

    async def list_all_changes(self):
        """List all available GitHub changes summaries."""
        try:
            keys = await self._observations.list(kind="github_changes")
            
            # Transform keys into a more user-friendly format
            changes_list = []
            for key in keys:
                # Extract repository name from the key
                # Key format: "owner/repo/changes_7d"
                key_parts = key.key.split("/")
                if len(key_parts) >= 3:
                    repo_name = "/".join(key_parts[:-1])  # Everything except the last part
                    period = key_parts[-1]  # e.g., "changes_7d"
                    
                    changes_list.append({
                        "repository": repo_name,
                        "period": period,
                        "name": key.name,
                        "key": key.key
                    })
            
            return {
                "changes": changes_list,
                "total": len(changes_list)
            }
            
        except Exception as e:
            _log.error(s_("Failed to list GitHub changes"), exc_info=e)
            raise HTTPException(status_code=500, detail="Failed to retrieve changes list")

    async def get_repo_changes(self, repo_id: str, days: int = 7):
        """Get changes summary for a specific repository."""
        try:
            # Get repository info to construct the key
            repo = await self._storage.get_github_repo(repo_id)
            if repo is None:
                raise HTTPException(status_code=404, detail=f"Repository {repo_id} not found")
            
            # Construct observation key
            observation_key = ObservationKey(
                kind="github_changes",
                name="changes_summary",
                key=f"{repo.full_name}/changes_{days}d"
            )
            
            try:
                observation = await self._observations.get(observation_key)
                return {
                    "repository": repo.full_name,
                    "period_days": days,
                    "summary": observation.content,
                    "last_updated": self._clock.now().isoformat()
                }
            except Exception:
                # If no changes summary exists, return empty result
                return {
                    "repository": repo.full_name,
                    "period_days": days,
                    "summary": None,
                    "message": "No changes summary available. Analysis may not have run yet."
                }
                
        except HTTPException:
            raise
        except Exception as e:
            _log.error(s_("Failed to get repository changes", repo_id=repo_id), exc_info=e)
            raise HTTPException(status_code=500, detail="Failed to retrieve repository changes")

    async def trigger_analysis(self, repo_id: str):
        """Trigger changes analysis for a specific repository."""
        try:
            # Get repository info
            repo = await self._storage.get_github_repo(repo_id)
            if repo is None:
                raise HTTPException(status_code=404, detail=f"Repository {repo_id} not found")
            
            # Trigger repository processing by setting next processing time to now
            from dev_observer.api.types.processing_pb2 import ProcessingItemKey
            await self._storage.set_next_processing_time(
                ProcessingItemKey(github_repo_id=repo_id), 
                self._clock.now()
            )
            
            return {
                "repository": repo.full_name,
                "message": "Changes analysis triggered successfully",
                "triggered_at": self._clock.now().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            _log.error(s_("Failed to trigger changes analysis", repo_id=repo_id), exc_info=e)
            raise HTTPException(status_code=500, detail="Failed to trigger changes analysis")