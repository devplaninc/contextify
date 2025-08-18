from dev_observer.api.types.repo_pb2 import GitRepository, GitProvider


def get_repo_key_pref(repo: GitRepository) -> str:
    return f"{get_git_provider_key_pref(repo.provider)}{repo.full_name}"


def get_repo_owner_key_pref(provider: GitProvider, owner: str) -> str:
    return f"{get_git_provider_key_pref(provider)}{owner}/"


def get_git_provider_key_pref(provider: GitProvider) -> str:
    if provider == GitProvider.GITHUB:
        return ""
    return f"__{get_git_provider_name(provider)}/"


def get_git_provider_name(provider: GitProvider) -> str:
    match provider:
        case GitProvider.GITHUB:
            return "github"
        case GitProvider.BIT_BUCKET:
            return "bit_bucket"
    name: str = GitProvider.Name(provider)
    return name.lower()
