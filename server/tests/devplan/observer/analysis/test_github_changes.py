import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from dataclasses import dataclass

from dev_observer.analysis.github_changes import GitHubChangesAnalyzer, CommitChange, ChangesSummary
from dev_observer.repository.types import ObservedRepo
from dev_observer.api.types.repo_pb2 import GitHubRepository


@dataclass
class MockCommit:
    """Mock GitHub commit object."""
    sha: str
    html_url: str
    commit: Mock
    files: list


@dataclass
class MockFile:
    """Mock GitHub file object."""
    filename: str
    additions: int
    deletions: int


class TestGitHubChangesAnalyzer:
    """Test cases for GitHubChangesAnalyzer."""

    @pytest.fixture
    def mock_auth_provider(self):
        """Mock auth provider."""
        auth_provider = AsyncMock()
        auth_provider.get_auth.return_value = Mock()
        return auth_provider

    @pytest.fixture
    def analyzer(self, mock_auth_provider):
        """Create analyzer instance."""
        return GitHubChangesAnalyzer(mock_auth_provider)

    @pytest.fixture
    def mock_repo(self):
        """Mock observed repository."""
        github_repo = GitHubRepository(
            id="test-repo-id",
            full_name="owner/test-repo",
            name="test-repo",
            url="https://github.com/owner/test-repo"
        )
        return ObservedRepo(
            url="https://github.com/owner/test-repo",
            github_repo=github_repo
        )

    def create_mock_commit(self, sha: str, message: str, author: str, date: datetime, files: list):
        """Create a mock commit with the given properties."""
        mock_commit = MockCommit(
            sha=sha,
            html_url=f"https://github.com/owner/test-repo/commit/{sha}",
            commit=Mock(),
            files=[MockFile(filename=f['filename'], additions=f['additions'], deletions=f['deletions']) for f in files]
        )
        
        # Set up commit.commit properties
        mock_commit.commit.message = message
        mock_commit.commit.author = Mock()
        mock_commit.commit.author.name = author
        mock_commit.commit.author.date = date
        
        return mock_commit

    @pytest.mark.asyncio
    async def test_analyze_recent_changes_success(self, analyzer, mock_repo, mock_auth_provider):
        """Test successful analysis of recent changes."""
        # Setup mock data
        now = datetime.now()
        commits_data = [
            {
                'sha': 'abc123',
                'message': 'Add new feature',
                'author': 'John Doe',
                'date': now - timedelta(days=1),
                'files': [
                    {'filename': 'src/main.py', 'additions': 10, 'deletions': 2},
                    {'filename': 'tests/test_main.py', 'additions': 5, 'deletions': 0}
                ]
            },
            {
                'sha': 'def456',
                'message': 'Fix bug in authentication',
                'author': 'Jane Smith',
                'date': now - timedelta(days=2),
                'files': [
                    {'filename': 'src/auth.py', 'additions': 3, 'deletions': 1}
                ]
            }
        ]
        
        mock_commits = [
            self.create_mock_commit(
                commit['sha'], 
                commit['message'], 
                commit['author'], 
                commit['date'], 
                commit['files']
            ) for commit in commits_data
        ]

        # Mock GitHub API calls
        with patch('dev_observer.analysis.github_changes.Github') as mock_github:
            mock_gh_instance = Mock()
            mock_github.return_value.__enter__.return_value = mock_gh_instance
            
            mock_gh_repo = Mock()
            mock_gh_instance.get_repo.return_value = mock_gh_repo
            mock_gh_repo.get_commits.return_value = mock_commits
            
            # Run the analysis
            result = await analyzer.analyze_recent_changes(mock_repo, days_back=7)
            
            # Verify results
            assert isinstance(result, ChangesSummary)
            assert result.repo_full_name == "owner/test-repo"
            assert result.total_commits == 2
            assert result.total_files_changed == 3  # main.py, test_main.py, auth.py
            assert result.total_additions == 18  # 10 + 5 + 3
            assert result.total_deletions == 3   # 2 + 0 + 1
            
            # Check commits
            assert len(result.commits) == 2
            assert result.commits[0].sha == 'abc123'
            assert result.commits[0].author == 'John Doe'
            assert result.commits[1].sha == 'def456'
            assert result.commits[1].author == 'Jane Smith'
            
            # Check contributors
            assert len(result.top_contributors) == 2
            john_contributor = next(c for c in result.top_contributors if c['name'] == 'John Doe')
            assert john_contributor['commits'] == 1
            assert john_contributor['additions'] == 15
            assert john_contributor['deletions'] == 2
            
            # Check most changed files
            assert len(result.most_changed_files) == 3
            main_py_file = next(f for f in result.most_changed_files if f['filename'] == 'src/main.py')
            assert main_py_file['changes'] == 1

    @pytest.mark.asyncio
    async def test_analyze_recent_changes_no_commits(self, analyzer, mock_repo, mock_auth_provider):
        """Test analysis when no commits are found."""
        with patch('dev_observer.analysis.github_changes.Github') as mock_github:
            mock_gh_instance = Mock()
            mock_github.return_value.__enter__.return_value = mock_gh_instance
            
            mock_gh_repo = Mock()
            mock_gh_instance.get_repo.return_value = mock_gh_repo
            mock_gh_repo.get_commits.return_value = []  # No commits
            
            result = await analyzer.analyze_recent_changes(mock_repo, days_back=7)
            
            assert result.total_commits == 0
            assert result.total_files_changed == 0
            assert result.total_additions == 0
            assert result.total_deletions == 0
            assert len(result.commits) == 0
            assert len(result.top_contributors) == 0
            assert len(result.most_changed_files) == 0

    def test_format_changes_summary(self, analyzer):
        """Test formatting of changes summary."""
        # Create a sample changes summary
        now = datetime.now()
        summary = ChangesSummary(
            repo_full_name="owner/test-repo",
            period_start=now - timedelta(days=7),
            period_end=now,
            total_commits=2,
            total_files_changed=3,
            total_additions=18,
            total_deletions=3,
            commits=[
                CommitChange(
                    sha="abc123",
                    message="Add new feature",
                    author="John Doe",
                    date=now - timedelta(days=1),
                    files_changed=["src/main.py", "tests/test_main.py"],
                    additions=15,
                    deletions=2,
                    url="https://github.com/owner/test-repo/commit/abc123"
                )
            ],
            top_contributors=[
                {'name': 'John Doe', 'commits': 1, 'additions': 15, 'deletions': 2}
            ],
            most_changed_files=[
                {'filename': 'src/main.py', 'changes': 1}
            ]
        )
        
        formatted = analyzer.format_changes_summary(summary)
        
        # Check that the formatted output contains expected sections
        assert "# GitHub Changes Summary for owner/test-repo" in formatted
        assert "## Overview" in formatted
        assert "- **Total Commits:** 2" in formatted
        assert "- **Files Changed:** 3" in formatted
        assert "- **Lines Added:** 18" in formatted
        assert "- **Lines Deleted:** 3" in formatted
        assert "## Top Contributors" in formatted
        assert "**John Doe**: 1 commits" in formatted
        assert "## Most Changed Files" in formatted
        assert "`src/main.py`: 1 changes" in formatted
        assert "## Recent Commits" in formatted
        assert "**abc123** by John Doe" in formatted

    @pytest.mark.asyncio
    async def test_analyze_recent_changes_error_handling(self, analyzer, mock_repo, mock_auth_provider):
        """Test error handling during analysis."""
        with patch('dev_observer.analysis.github_changes.Github') as mock_github:
            mock_gh_instance = Mock()
            mock_github.return_value.__enter__.return_value = mock_gh_instance
            mock_gh_instance.get_repo.side_effect = Exception("GitHub API error")
            
            with pytest.raises(Exception, match="GitHub API error"):
                await analyzer.analyze_recent_changes(mock_repo, days_back=7)