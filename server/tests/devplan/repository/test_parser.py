import unittest

from dev_observer.api.types.repo_pb2 import GitProvider
from dev_observer.repository.parser import parse_github_url, parse_repository_url, ParsedRepoUrl, _parse_github_url, \
    _parse_bitbucket_url


class TestParseGithubUrl(unittest.TestCase):
    def test_ssh_url(self):
        # Test SSH URL format
        url = "git@github.com:owner/repo"
        result = parse_github_url(url)
        self.assertEqual(result.owner, "owner")
        self.assertEqual(result.name, "repo")
        self.assertEqual(result.get_full_name(), "owner/repo")

    def test_https_url(self):
        # Test HTTPS URL format
        url = "https://github.com/owner/repo"
        result = parse_github_url(url)
        self.assertEqual(result.owner, "owner")
        self.assertEqual(result.name, "repo")
        self.assertEqual(result.get_full_name(), "owner/repo")

    def test_http_url(self):
        # Test HTTP URL format
        url = "http://github.com/owner/repo"
        result = parse_github_url(url)
        self.assertEqual(result.owner, "owner")
        self.assertEqual(result.name, "repo")

    def test_url_with_trailing_slash(self):
        # Test URL with trailing slash
        url = "https://github.com/owner/repo/"
        result = parse_github_url(url)
        self.assertEqual(result.owner, "owner")
        self.assertEqual(result.name, "repo")

    def test_cli_url(self):
        # Test URL with trailing slash
        url = "https://github.com/devplaninc/devplan-cli"
        result = parse_github_url(url)
        self.assertEqual(result.owner, "devplaninc")
        self.assertEqual(result.name, "devplan-cli")
        self.assertEqual(result.get_full_name(), "devplaninc/devplan-cli")

    def test_url_with_git_extension(self):
        # Test URL with .git extension
        url = "https://github.com/owner/repo.git"
        result = parse_github_url(url)
        self.assertEqual(result.owner, "owner")
        self.assertEqual(result.name, "repo")

    def test_ssh_url_with_git_extension(self):
        # Test SSH URL with .git extension
        url = "git@github.com:owner/repo.git"
        result = parse_github_url(url)
        self.assertEqual(result.owner, "owner")
        self.assertEqual(result.name, "repo")

    def test_invalid_ssh_url(self):
        # Test invalid SSH URL format
        with self.assertRaises(ValueError):
            parse_github_url("git@github.com:invalid")

    def test_invalid_https_url(self):
        # Test invalid HTTPS URL format
        with self.assertRaises(ValueError):
            parse_github_url("https://github.com/invalid")

    def test_non_github_url(self):
        # Test non-GitHub URL
        with self.assertRaises(ValueError):
            parse_github_url("https://gitlab.com/owner/repo")

    def test_empty_url(self):
        # Test empty URL
        with self.assertRaises(ValueError):
            parse_github_url("")

    def test_parsed_repo_url_class(self):
        # Test ParsedRepoUrl class
        repo = ParsedRepoUrl(owner="owner", name="repo")
        self.assertEqual(repo.owner, "owner")
        self.assertEqual(repo.name, "repo")
        self.assertEqual(repo.get_full_name(), "owner/repo")


class TestParseRepositoryUrl(unittest.TestCase):
    """Test cases for the parse_repository_url function."""

    def test_github_https_url(self):
        """Test GitHub HTTPS URL parsing."""
        url = "https://github.com/owner/repo"
        result = parse_repository_url(url, GitProvider.GITHUB)
        self.assertEqual(result.owner, "owner")
        self.assertEqual(result.name, "repo")
        self.assertEqual(result.get_full_name(), "owner/repo")

    def test_github_https_url_with_trailing_slash(self):
        """Test GitHub HTTPS URL with trailing slash."""
        url = "https://github.com/owner/repo/"
        result = parse_repository_url(url, GitProvider.GITHUB)
        self.assertEqual(result.owner, "owner")
        self.assertEqual(result.name, "repo")

    def test_github_https_url_with_git_extension(self):
        """Test GitHub HTTPS URL with .git extension."""
        url = "https://github.com/owner/repo.git"
        result = parse_repository_url(url, GitProvider.GITHUB)
        self.assertEqual(result.owner, "owner")
        self.assertEqual(result.name, "repo")

    def test_github_ssh_url(self):
        """Test GitHub SSH URL parsing."""
        url = "git@github.com:owner/repo.git"
        result = parse_repository_url(url, GitProvider.GITHUB)
        self.assertEqual(result.owner, "owner")
        self.assertEqual(result.name, "repo")

    def test_github_complex_names(self):
        """Test GitHub URLs with complex owner/repo names."""
        url = "https://github.com/my-org/my-repo-name"
        result = parse_repository_url(url, GitProvider.GITHUB)
        self.assertEqual(result.owner, "my-org")
        self.assertEqual(result.name, "my-repo-name")

    def test_bitbucket_https_url(self):
        """Test BitBucket HTTPS URL parsing."""
        url = "https://bitbucket.org/owner/repo"
        result = parse_repository_url(url, GitProvider.BIT_BUCKET)
        self.assertEqual(result.owner, "owner")
        self.assertEqual(result.name, "repo")
        self.assertEqual(result.get_full_name(), "owner/repo")

    def test_bitbucket_https_url_with_trailing_slash(self):
        """Test BitBucket HTTPS URL with trailing slash."""
        url = "https://bitbucket.org/owner/repo/"
        result = parse_repository_url(url, GitProvider.BIT_BUCKET)
        self.assertEqual(result.owner, "owner")
        self.assertEqual(result.name, "repo")

    def test_bitbucket_https_url_with_git_extension(self):
        """Test BitBucket HTTPS URL with .git extension."""
        url = "https://bitbucket.org/owner/repo.git"
        result = parse_repository_url(url, GitProvider.BIT_BUCKET)
        self.assertEqual(result.owner, "owner")
        self.assertEqual(result.name, "repo")

    def test_bitbucket_ssh_url(self):
        """Test BitBucket SSH URL parsing."""
        url = "git@bitbucket.org:owner/repo.git"
        result = parse_repository_url(url, GitProvider.BIT_BUCKET)
        self.assertEqual(result.owner, "owner")
        self.assertEqual(result.name, "repo")

    def test_bitbucket_complex_names(self):
        """Test BitBucket URLs with complex owner/repo names."""
        url = "https://bitbucket.org/my-org/my-repo-name"
        result = parse_repository_url(url, GitProvider.BIT_BUCKET)
        self.assertEqual(result.owner, "my-org")
        self.assertEqual(result.name, "my-repo-name")

    def test_unsupported_provider(self):
        """Test unsupported Git provider."""
        url = "https://github.com/owner/repo"
        with self.assertRaises(ValueError) as context:
            parse_repository_url(url, 999)  # Invalid provider value
        self.assertIn("Unsupported Git provider", str(context.exception))

    def test_invalid_github_ssh_url(self):
        """Test invalid GitHub SSH URL format."""
        with self.assertRaises(ValueError) as context:
            parse_repository_url("git@github.com:invalid", GitProvider.GITHUB)
        self.assertIn("Invalid GitHub URL", str(context.exception))

    def test_invalid_github_https_url(self):
        """Test invalid GitHub HTTPS URL format."""
        with self.assertRaises(ValueError) as context:
            parse_repository_url("https://github.com/invalid", GitProvider.GITHUB)
        self.assertIn("Invalid GitHub URL", str(context.exception))

    def test_invalid_bitbucket_ssh_url(self):
        """Test invalid BitBucket SSH URL format."""
        with self.assertRaises(ValueError) as context:
            parse_repository_url("git@bitbucket.org:invalid", GitProvider.BIT_BUCKET)
        self.assertIn("Invalid BitBucket URL", str(context.exception))

    def test_invalid_bitbucket_https_url(self):
        """Test invalid BitBucket HTTPS URL format."""
        with self.assertRaises(ValueError) as context:
            parse_repository_url("https://bitbucket.org/invalid", GitProvider.BIT_BUCKET)
        self.assertIn("Invalid BitBucket URL", str(context.exception))

    def test_wrong_provider_for_github_url(self):
        """Test GitHub URL with BitBucket provider."""
        url = "https://github.com/owner/repo"
        with self.assertRaises(ValueError) as context:
            parse_repository_url(url, GitProvider.BIT_BUCKET)
        self.assertIn("Invalid BitBucket URL", str(context.exception))

    def test_wrong_provider_for_bitbucket_url(self):
        """Test BitBucket URL with GitHub provider."""
        url = "https://bitbucket.org/owner/repo"
        with self.assertRaises(ValueError) as context:
            parse_repository_url(url, GitProvider.GITHUB)
        self.assertIn("Invalid GitHub URL", str(context.exception))


class TestParseGithubUrlHelper(unittest.TestCase):
    """Test cases for the _parse_github_url helper function."""

    def test_github_ssh_url(self):
        """Test GitHub SSH URL parsing."""
        url = "git@github.com:owner/repo"
        result = _parse_github_url(url)
        self.assertEqual(result.owner, "owner")
        self.assertEqual(result.name, "repo")

    def test_github_https_url(self):
        """Test GitHub HTTPS URL parsing."""
        url = "https://github.com/owner/repo"
        result = _parse_github_url(url)
        self.assertEqual(result.owner, "owner")
        self.assertEqual(result.name, "repo")

    def test_github_http_url(self):
        """Test GitHub HTTP URL parsing."""
        url = "http://github.com/owner/repo"
        result = _parse_github_url(url)
        self.assertEqual(result.owner, "owner")
        self.assertEqual(result.name, "repo")

    def test_invalid_ssh_format(self):
        """Test invalid SSH URL format."""
        with self.assertRaises(ValueError):
            _parse_github_url("git@github.com:owner")

    def test_invalid_https_format(self):
        """Test invalid HTTPS URL format."""
        with self.assertRaises(ValueError):
            _parse_github_url("https://github.com/owner")

    def test_non_github_domain(self):
        """Test non-GitHub domain."""
        with self.assertRaises(ValueError):
            _parse_github_url("https://gitlab.com/owner/repo")


class TestParseBitbucketUrlHelper(unittest.TestCase):
    """Test cases for the _parse_bitbucket_url helper function."""

    def test_bitbucket_ssh_url(self):
        """Test BitBucket SSH URL parsing."""
        url = "git@bitbucket.org:owner/repo"
        result = _parse_bitbucket_url(url)
        self.assertEqual(result.owner, "owner")
        self.assertEqual(result.name, "repo")

    def test_bitbucket_https_url(self):
        """Test BitBucket HTTPS URL parsing."""
        url = "https://bitbucket.org/owner/repo"
        result = _parse_bitbucket_url(url)
        self.assertEqual(result.owner, "owner")
        self.assertEqual(result.name, "repo")

    def test_bitbucket_http_url(self):
        """Test BitBucket HTTP URL parsing."""
        url = "http://bitbucket.org/owner/repo"
        result = _parse_bitbucket_url(url)
        self.assertEqual(result.owner, "owner")
        self.assertEqual(result.name, "repo")

    def test_invalid_ssh_format(self):
        """Test invalid SSH URL format."""
        with self.assertRaises(ValueError):
            _parse_bitbucket_url("git@bitbucket.org:owner")

    def test_invalid_https_format(self):
        """Test invalid HTTPS URL format."""
        with self.assertRaises(ValueError):
            _parse_bitbucket_url("https://bitbucket.org/owner")

    def test_non_bitbucket_domain(self):
        """Test non-BitBucket domain."""
        with self.assertRaises(ValueError):
            _parse_bitbucket_url("https://github.com/owner/repo")
