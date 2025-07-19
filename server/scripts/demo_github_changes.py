#!/usr/bin/env python3
"""
Test script for GitHub changes analysis functionality.

This script demonstrates and tests the GitHub changes analysis feature.
"""

import asyncio
import logging
import os
from datetime import datetime

from dev_observer.analysis.github_changes import GitHubChangesAnalyzer
from dev_observer.processors.changes import ChangesProcessor
from dev_observer.repository.auth.github_token import GithubTokenAuthProvider
from dev_observer.repository.types import ObservedRepo
from dev_observer.api.types.repo_pb2 import GitHubRepository
from dev_observer.api.types.config_pb2 import GlobalConfig
from dev_observer.observations.memory import MemoryObservationsProvider

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_github_changes_analysis():
    """Test the GitHub changes analysis functionality."""
    
    # Check for GitHub token
    github_token = os.getenv("GITHUB_TOKEN") or os.getenv("DEV_OBSERVER__GIT__GITHUB__PERSONAL_TOKEN")
    if not github_token:
        logger.error("GitHub token not found. Please set GITHUB_TOKEN or DEV_OBSERVER__GIT__GITHUB__PERSONAL_TOKEN environment variable.")
        return False
    
    logger.info("Testing GitHub changes analysis functionality...")
    
    try:
        # Set up components
        auth_provider = GithubTokenAuthProvider(github_token)
        changes_analyzer = GitHubChangesAnalyzer(auth_provider)
        observations_provider = MemoryObservationsProvider()
        changes_processor = ChangesProcessor(changes_analyzer, observations_provider)
        
        # Create a test repository (using a well-known public repo)
        test_repo = ObservedRepo(
            url="https://github.com/octocat/Hello-World",
            github_repo=GitHubRepository(
                id="test-repo-id",
                full_name="octocat/Hello-World",
                name="Hello-World",
                url="https://github.com/octocat/Hello-World"
            )
        )
        
        logger.info(f"Analyzing changes for repository: {test_repo.github_repo.full_name}")
        
        # Test 1: Direct analyzer usage
        logger.info("Test 1: Testing GitHubChangesAnalyzer directly...")
        changes_summary = await changes_analyzer.analyze_recent_changes(test_repo, days_back=30)
        
        logger.info(f"Analysis results:")
        logger.info(f"  - Total commits: {changes_summary.total_commits}")
        logger.info(f"  - Files changed: {changes_summary.total_files_changed}")
        logger.info(f"  - Lines added: {changes_summary.total_additions}")
        logger.info(f"  - Lines deleted: {changes_summary.total_deletions}")
        logger.info(f"  - Top contributors: {len(changes_summary.top_contributors)}")
        
        # Test 2: Formatted output
        logger.info("Test 2: Testing formatted output...")
        formatted_report = changes_analyzer.format_changes_summary(changes_summary)
        logger.info("Formatted report preview (first 500 chars):")
        logger.info(formatted_report[:500] + "..." if len(formatted_report) > 500 else formatted_report)
        
        # Test 3: Changes processor
        logger.info("Test 3: Testing ChangesProcessor...")
        config = GlobalConfig()  # Use default config
        await changes_processor.process_repository_changes(test_repo, config, days_back=30)
        
        # Verify observation was stored
        from dev_observer.api.types.observations_pb2 import ObservationKey
        observation_key = ObservationKey(
            kind="github_changes",
            name="changes_summary",
            key=f"{test_repo.github_repo.full_name}/changes_30d"
        )
        
        stored_observation = await observations_provider.get(observation_key)
        logger.info(f"Stored observation content length: {len(stored_observation.content)} characters")
        
        # Test 4: List observations
        logger.info("Test 4: Testing observation listing...")
        observation_keys = await observations_provider.list("github_changes")
        logger.info(f"Found {len(observation_keys)} GitHub changes observations")
        for key in observation_keys:
            logger.info(f"  - {key.kind}/{key.name}/{key.key}")
        
        logger.info("✅ All tests passed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}", exc_info=True)
        return False


async def test_error_handling():
    """Test error handling with invalid repository."""
    logger.info("Testing error handling...")
    
    github_token = os.getenv("GITHUB_TOKEN") or os.getenv("DEV_OBSERVER__GIT__GITHUB__PERSONAL_TOKEN")
    if not github_token:
        logger.info("Skipping error handling test - no GitHub token")
        return True
    
    try:
        auth_provider = GithubTokenAuthProvider(github_token)
        changes_analyzer = GitHubChangesAnalyzer(auth_provider)
        
        # Create an invalid repository
        invalid_repo = ObservedRepo(
            url="https://github.com/nonexistent/invalid-repo-12345",
            github_repo=GitHubRepository(
                id="invalid-repo-id",
                full_name="nonexistent/invalid-repo-12345",
                name="invalid-repo-12345",
                url="https://github.com/nonexistent/invalid-repo-12345"
            )
        )
        
        # This should raise an exception
        await changes_analyzer.analyze_recent_changes(invalid_repo, days_back=7)
        logger.error("❌ Expected exception for invalid repository, but none was raised")
        return False
        
    except Exception as e:
        logger.info(f"✅ Error handling test passed - caught expected exception: {type(e).__name__}")
        return True


def main():
    """Main function to run all tests."""
    logger.info("Starting GitHub changes analysis tests...")
    
    async def run_tests():
        success = True
        
        # Run main functionality test
        if not await test_github_changes_analysis():
            success = False
        
        # Run error handling test
        if not await test_error_handling():
            success = False
        
        return success
    
    # Run the tests
    success = asyncio.run(run_tests())
    
    if success:
        logger.info("🎉 All tests completed successfully!")
        exit(0)
    else:
        logger.error("💥 Some tests failed!")
        exit(1)


if __name__ == "__main__":
    main()