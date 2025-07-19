import logging
from typing import List

from dev_observer.analysis.github_changes import GitHubChangesAnalyzer
from dev_observer.api.types.config_pb2 import GlobalConfig
from dev_observer.api.types.observations_pb2 import ObservationKey, Observation
from dev_observer.log import s_
from dev_observer.observations.provider import ObservationsProvider
from dev_observer.repository.types import ObservedRepo

_log = logging.getLogger(__name__)


class ChangesProcessor:
    """Processes GitHub repository changes and stores analysis results."""
    
    def __init__(
        self,
        changes_analyzer: GitHubChangesAnalyzer,
        observations: ObservationsProvider,
    ):
        self.changes_analyzer = changes_analyzer
        self.observations = observations
    
    async def process_repository_changes(
        self, 
        repo: ObservedRepo, 
        config: GlobalConfig,
        days_back: int = 7
    ):
        """
        Process changes for a repository and store the analysis results.
        
        Args:
            repo: The repository to analyze
            config: Global configuration
            days_back: Number of days to look back for changes
        """
        try:
            _log.info(s_("Processing repository changes", repo=repo.github_repo.full_name, days_back=days_back))
            
            # Analyze recent changes
            changes_summary = await self.changes_analyzer.analyze_recent_changes(repo, days_back)
            
            # Format the summary as a readable report
            formatted_report = self.changes_analyzer.format_changes_summary(changes_summary)
            
            # Store the changes summary as an observation
            observation_key = ObservationKey(
                kind="github_changes",
                name="changes_summary",
                key=f"{repo.github_repo.full_name}/changes_{days_back}d"
            )
            
            observation = Observation(
                key=observation_key,
                content=formatted_report
            )
            
            await self.observations.store(observation)
            
            _log.info(s_("Repository changes processed successfully", 
                       repo=repo.github_repo.full_name,
                       commits=changes_summary.total_commits,
                       files_changed=changes_summary.total_files_changed))
            
        except Exception as e:
            _log.error(s_("Failed to process repository changes", 
                         repo=repo.github_repo.full_name), exc_info=e)
            raise