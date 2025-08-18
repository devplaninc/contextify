import unittest

from server.src.dev_observer.api.types.repo_pb2 import GitRepository, GitProvider
from server.src.dev_observer.processors.observations import get_repo_key_pref, get_repo_owner_key_pref


class TestGetKeyPref(unittest.TestCase):

    def test_github_provider(self):
        repo = GitRepository(
            name="example-repo",
            full_name="example-org/example-repo",
            url="https://github.com/example-org/example-repo",
            provider=GitProvider.GITHUB,
        )
        self.assertEqual("example-org/example-repo", get_repo_key_pref(repo))

    def test_non_github_provider(self):
        repo = GitRepository(
            name="another-repo",
            full_name="another-org/another-repo",
            url="https://bitbucket.org/another-org/another-repo",
            provider=GitProvider.BIT_BUCKET,
        )
        self.assertEqual("__bit_bucket/another-org/another-repo", get_repo_key_pref(repo))

    def test_empty_full_name(self):
        repo = GitRepository(
            name="empty-repo",
            full_name="",
            url="https://bitbucket.org/empty-org/empty-repo",
            provider=GitProvider.BIT_BUCKET,
        )
        self.assertEqual("__bit_bucket/", get_repo_key_pref(repo))

    def test_owner_pref(self):
        self.assertEqual("example-org/", get_repo_owner_key_pref(GitProvider.GITHUB, "example-org"))
        self.assertEqual("__bit_bucket/example-org/", get_repo_owner_key_pref(GitProvider.BIT_BUCKET, "example-org"))
