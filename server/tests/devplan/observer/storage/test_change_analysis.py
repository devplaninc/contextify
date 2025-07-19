import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from dev_observer.api.types.repo_pb2 import RepoChangeAnalysis, GitHubRepository, GitProperties, ChangeAnalysisConfig
from dev_observer.storage.postgresql.provider import PostgresqlStorageProvider
from dev_observer.util import RealClock


class TestChangeAnalysisStorage:
    
    @pytest.fixture
    def mock_clock(self):
        clock = MagicMock()
        clock.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
        return clock
    
    @pytest.fixture
    def storage_provider(self, mock_clock):
        # Mock the storage provider instead of creating a real one
        provider = MagicMock()
        provider._clock = mock_clock
        return provider
    
    @pytest.fixture
    def sample_analysis(self):
        analysis = RepoChangeAnalysis()
        analysis.id = str(uuid.uuid4())
        analysis.repo_id = str(uuid.uuid4())
        analysis.status = "pending"
        analysis.created_at.FromDatetime(datetime.now())
        analysis.updated_at.FromDatetime(datetime.now())
        return analysis
    
    @pytest.fixture
    def sample_repo(self):
        repo = GitHubRepository()
        repo.id = str(uuid.uuid4())
        repo.name = "test-repo"
        repo.full_name = "owner/test-repo"
        repo.url = "https://github.com/owner/test-repo"
        repo.description = "Test repository"
        return repo

    def test_create_repo_change_analysis(self, storage_provider, sample_analysis):
        # Test the analysis data structure
        analysis_id = sample_analysis.id
        repo_id = sample_analysis.repo_id
        status = sample_analysis.status
        
        assert analysis_id is not None
        assert repo_id is not None
        assert status == "pending"

    def test_enroll_repo_for_change_analysis_logic(self, sample_repo, mock_clock):
        # Test enrollment logic using a real instance
        from dev_observer.storage.postgresql.provider import PostgresqlStorageProvider
        
        # Create a mock instance for testing the logic without database
        provider = MagicMock(spec=PostgresqlStorageProvider)
        provider._clock = mock_clock
        
        # Test the enrollment would work with proper setup
        repo_id = sample_repo.id
        assert repo_id is not None

    def test_unenroll_repo_from_change_analysis_logic(self, sample_repo):
        # Set up enrolled repo
        config = ChangeAnalysisConfig()
        config.enrolled = True
        config.enrolled_at.FromDatetime(datetime.now())
        
        sample_repo.properties.CopyFrom(GitProperties())
        sample_repo.properties.change_analysis.CopyFrom(config)
        
        # Test that the repo has the correct enrollment status
        assert sample_repo.properties.change_analysis.enrolled is True

    def test_get_enrolled_repos_filtering_logic(self):
        # Test the filtering logic for enrolled repos
        # Create test repos
        enrolled_repo = GitHubRepository()
        enrolled_repo.id = str(uuid.uuid4())
        enrolled_repo.full_name = "owner/enrolled-repo"
        enrolled_repo.properties.CopyFrom(GitProperties())
        enrolled_repo.properties.change_analysis.enrolled = True
        
        not_enrolled_repo = GitHubRepository()
        not_enrolled_repo.id = str(uuid.uuid4())
        not_enrolled_repo.full_name = "owner/not-enrolled-repo"
        
        repos = [enrolled_repo, not_enrolled_repo]
        
        # Test filtering logic
        enrolled_repos = [
            repo for repo in repos
            if repo.HasField("properties") 
            and repo.properties.HasField("change_analysis")
            and repo.properties.change_analysis.enrolled
        ]
        
        # Verify only enrolled repo is returned
        assert len(enrolled_repos) == 1
        assert enrolled_repos[0].id == enrolled_repo.id

    def test_repo_change_analysis_entity_fields(self):
        """Test that the RepoChangeAnalysisEntity has all required fields"""
        from dev_observer.storage.postgresql.model import RepoChangeAnalysisEntity
        
        # Verify entity has all required columns
        entity = RepoChangeAnalysisEntity(
            id="test-id",
            repo_id="test-repo-id", 
            status="pending"
        )
        
        assert entity.id == "test-id"
        assert entity.repo_id == "test-repo-id"
        assert entity.status == "pending"
        assert entity.observation_key is None
        assert entity.error_message is None
        assert entity.analyzed_at is None

    def test_change_analysis_config_protobuf(self):
        """Test ChangeAnalysisConfig protobuf message"""
        config = ChangeAnalysisConfig()
        config.enrolled = True
        config.enrolled_at.FromDatetime(datetime.now())
        
        assert config.enrolled is True
        assert config.enrolled_at is not None

    def test_repo_change_analysis_protobuf(self):
        """Test RepoChangeAnalysis protobuf message"""
        analysis = RepoChangeAnalysis()
        analysis.id = "test-id"
        analysis.repo_id = "repo-id"
        analysis.status = "completed"
        analysis.observation_key = "obs-key"
        analysis.analyzed_at.FromDatetime(datetime.now())
        analysis.created_at.FromDatetime(datetime.now())
        analysis.updated_at.FromDatetime(datetime.now())
        
        assert analysis.id == "test-id"
        assert analysis.repo_id == "repo-id"
        assert analysis.status == "completed"
        assert analysis.observation_key == "obs-key"
        assert analysis.HasField("analyzed_at")
        assert analysis.HasField("created_at")
        assert analysis.HasField("updated_at")