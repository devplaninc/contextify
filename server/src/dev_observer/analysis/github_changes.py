import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from github import Github, Commit
from github.Repository import Repository

from dev_observer.api.types.repo_pb2 import GitHubRepository
from dev_observer.repository.auth.github_token import GithubTokenAuthProvider
from dev_observer.repository.auth.github_app import GithubAppAuthProvider
from dev_observer.repository.types import ObservedRepo

_log = logging.getLogger(__name__)


@dataclass
class CommitChange:
    """Represents a single commit change."""
    sha: str
    message: str
    author: str
    date: datetime
    files_changed: List[str]
    additions: int
    deletions: int
    url: str


@dataclass
class ChangesSummary:
    """Summary of recent changes in a repository."""
    repo_full_name: str
    period_start: datetime
    period_end: datetime
    total_commits: int
    total_files_changed: int
    total_additions: int
    total_deletions: int
    commits: List[CommitChange]
    top_contributors: List[Dict[str, Any]]
    most_changed_files: List[Dict[str, Any]]


class GitHubChangesAnalyzer:
    """Analyzes recent changes in GitHub repositories."""
    
    def __init__(self, auth_provider):
        self.auth_provider = auth_provider
    
    async def analyze_recent_changes(
        self, 
        repo: ObservedRepo, 
        days_back: int = 7
    ) -> ChangesSummary:
        """
        Analyze recent changes in a GitHub repository.
        
        Args:
            repo: The observed repository
            days_back: Number of days to look back for changes
            
        Returns:
            ChangesSummary with analysis results
        """
        auth = await self.auth_provider.get_auth(repo)
        
        with Github(auth=auth) as gh:
            gh_repo = gh.get_repo(repo.github_repo.full_name)
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            _log.info(f"Analyzing changes for {repo.github_repo.full_name} from {start_date} to {end_date}")
            
            # Get commits in the date range
            commits = list(gh_repo.get_commits(since=start_date, until=end_date))
            
            # Process commits
            commit_changes = []
            all_files_changed = set()
            total_additions = 0
            total_deletions = 0
            contributors = {}
            file_change_counts = {}
            
            for commit in commits:
                try:
                    # Get commit details
                    files_in_commit = []
                    commit_additions = 0
                    commit_deletions = 0
                    
                    # Process files changed in this commit
                    for file in commit.files:
                        files_in_commit.append(file.filename)
                        all_files_changed.add(file.filename)
                        commit_additions += file.additions
                        commit_deletions += file.deletions
                        
                        # Track file change frequency
                        file_change_counts[file.filename] = file_change_counts.get(file.filename, 0) + 1
                    
                    total_additions += commit_additions
                    total_deletions += commit_deletions
                    
                    # Track contributors
                    author_name = commit.commit.author.name if commit.commit.author else "Unknown"
                    if author_name not in contributors:
                        contributors[author_name] = {
                            'name': author_name,
                            'commits': 0,
                            'additions': 0,
                            'deletions': 0
                        }
                    contributors[author_name]['commits'] += 1
                    contributors[author_name]['additions'] += commit_additions
                    contributors[author_name]['deletions'] += commit_deletions
                    
                    # Create commit change record
                    commit_change = CommitChange(
                        sha=commit.sha,
                        message=commit.commit.message.split('\n')[0][:100],  # First line, truncated
                        author=author_name,
                        date=commit.commit.author.date,
                        files_changed=files_in_commit,
                        additions=commit_additions,
                        deletions=commit_deletions,
                        url=commit.html_url
                    )
                    commit_changes.append(commit_change)
                    
                except Exception as e:
                    _log.warning(f"Error processing commit {commit.sha}: {e}")
                    continue
            
            # Sort contributors by number of commits
            top_contributors = sorted(
                contributors.values(), 
                key=lambda x: x['commits'], 
                reverse=True
            )[:10]
            
            # Sort files by change frequency
            most_changed_files = [
                {'filename': filename, 'changes': count}
                for filename, count in sorted(
                    file_change_counts.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:20]
            ]
            
            return ChangesSummary(
                repo_full_name=repo.github_repo.full_name,
                period_start=start_date,
                period_end=end_date,
                total_commits=len(commits),
                total_files_changed=len(all_files_changed),
                total_additions=total_additions,
                total_deletions=total_deletions,
                commits=commit_changes,
                top_contributors=top_contributors,
                most_changed_files=most_changed_files
            )
    
    def format_changes_summary(self, summary: ChangesSummary) -> str:
        """
        Format the changes summary into a readable text report.
        
        Args:
            summary: The changes summary to format
            
        Returns:
            Formatted text report
        """
        report = []
        report.append(f"# GitHub Changes Summary for {summary.repo_full_name}")
        report.append(f"**Period:** {summary.period_start.strftime('%Y-%m-%d')} to {summary.period_end.strftime('%Y-%m-%d')}")
        report.append("")
        
        # Overview
        report.append("## Overview")
        report.append(f"- **Total Commits:** {summary.total_commits}")
        report.append(f"- **Files Changed:** {summary.total_files_changed}")
        report.append(f"- **Lines Added:** {summary.total_additions}")
        report.append(f"- **Lines Deleted:** {summary.total_deletions}")
        report.append("")
        
        # Top Contributors
        if summary.top_contributors:
            report.append("## Top Contributors")
            for contributor in summary.top_contributors[:5]:
                report.append(f"- **{contributor['name']}**: {contributor['commits']} commits, "
                            f"+{contributor['additions']}/-{contributor['deletions']} lines")
            report.append("")
        
        # Most Changed Files
        if summary.most_changed_files:
            report.append("## Most Changed Files")
            for file_info in summary.most_changed_files[:10]:
                report.append(f"- `{file_info['filename']}`: {file_info['changes']} changes")
            report.append("")
        
        # Recent Commits
        if summary.commits:
            report.append("## Recent Commits")
            for commit in summary.commits[:10]:  # Show last 10 commits
                report.append(f"- **{commit.sha[:8]}** by {commit.author} ({commit.date.strftime('%Y-%m-%d %H:%M')})")
                report.append(f"  {commit.message}")
                report.append(f"  Files: {len(commit.files_changed)}, +{commit.additions}/-{commit.deletions}")
                report.append("")
        
        return "\n".join(report)