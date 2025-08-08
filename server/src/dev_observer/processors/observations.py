from dev_observer.api.types.repo_pb2 import GitRepository, GitProvider


def get_repo_key_pref(repo: GitRepository) -> str:
    if repo.provider == GitProvider.GITHUB:
        return repo.full_name
    return f"__{get_git_provider_name(repo.provider)}/{repo.full_name}"


def get_git_provider_name(provider: GitProvider) -> str:
    match provider:
        case GitProvider.GITHUB:
            return "github"
        case GitProvider.BIT_BUCKET:
            return "bit_bucket"
    name: str = GitProvider.Name(provider)
    return name.lower()

