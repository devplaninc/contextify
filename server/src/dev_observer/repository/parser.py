import dataclasses
from dev_observer.api.types.repo_pb2 import GitProvider


@dataclasses.dataclass
class ParsedRepoUrl:
    owner: str
    name: str

    def get_full_name(self) -> str:
        return f"{self.owner}/{self.name}"


def parse_repository_url(repo_url: str, provider: GitProvider) -> ParsedRepoUrl:
    """Parse repository URL for supported Git providers"""
    # Remove trailing slash if present
    repo_url = repo_url.rstrip('/')
    # Remove .git extension if present
    if repo_url.endswith('.git'):
        repo_url = repo_url[:-4]

    if provider == GitProvider.GITHUB:
        return _parse_github_url(repo_url)
    elif provider == GitProvider.BIT_BUCKET:
        return _parse_bitbucket_url(repo_url)
    else:
        raise ValueError(f"Unsupported Git provider: {provider}")


def _parse_github_url(github_url: str) -> ParsedRepoUrl:
    """Parse GitHub repository URL"""
    if github_url.startswith('git@github.com:'):
        parts = github_url.split(':')
        if len(parts) != 2:
            raise ValueError(f"Invalid GitHub URL: {github_url}")
        owner_repo = parts[1].split('/')
        if len(owner_repo) != 2:
            raise ValueError(f"Invalid GitHub URL: {github_url}")
        owner = owner_repo[0]
        repo_name = owner_repo[1]
    # Handle HTTPS and Git protocol formats
    else:
        parts = github_url.split('/')
        # Check if it's a valid GitHub URL
        if len(parts) < 3 or 'github.com' not in parts:
            raise ValueError(f"Invalid GitHub URL: {github_url}")

        # Find the index of 'github.com' in the parts
        github_index = parts.index('github.com')

        # Owner and repo should be right after 'github.com'
        if len(parts) < github_index + 3:
            raise ValueError(f"Invalid GitHub URL: {github_url}")

        owner = parts[github_index + 1]
        repo_name = parts[github_index + 2]

    return ParsedRepoUrl(owner, repo_name)


def _parse_bitbucket_url(bitbucket_url: str) -> ParsedRepoUrl:
    """Parse BitBucket repository URL"""
    if bitbucket_url.startswith('git@bitbucket.org:'):
        parts = bitbucket_url.split(':')
        if len(parts) != 2:
            raise ValueError(f"Invalid BitBucket URL: {bitbucket_url}")
        owner_repo = parts[1].split('/')
        if len(owner_repo) != 2:
            raise ValueError(f"Invalid BitBucket URL: {bitbucket_url}")
        owner = owner_repo[0]
        repo_name = owner_repo[1]
    # Handle HTTPS and Git protocol formats
    else:
        parts = bitbucket_url.split('/')
        # Check if it's a valid BitBucket URL
        if len(parts) < 3 or 'bitbucket.org' not in parts:
            raise ValueError(f"Invalid BitBucket URL: {bitbucket_url}")

        # Find the index of 'bitbucket.org' in the parts
        bitbucket_index = parts.index('bitbucket.org')

        # Owner and repo should be right after 'bitbucket.org'
        if len(parts) < bitbucket_index + 3:
            raise ValueError(f"Invalid BitBucket URL: {bitbucket_url}")

        owner = parts[bitbucket_index + 1]
        repo_name = parts[bitbucket_index + 2]

    return ParsedRepoUrl(owner, repo_name)


def parse_github_url(github_url: str) -> ParsedRepoUrl:
    """Legacy function for backward compatibility - defaults to GitHub"""
    return parse_repository_url(github_url, GitProvider.GITHUB)


