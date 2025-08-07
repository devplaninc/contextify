import { detectGitProvider } from '../repositoryUtils';
import { GitProvider } from '../../pb/dev_observer/api/types/repo';

describe('detectGitProvider', () => {
  describe('GitHub URLs', () => {
    test('should detect GitHub from HTTPS URL', () => {
      expect(detectGitProvider('https://github.com/owner/repo')).toBe(GitProvider.GITHUB);
    });

    test('should detect GitHub from HTTPS URL with trailing slash', () => {
      expect(detectGitProvider('https://github.com/owner/repo/')).toBe(GitProvider.GITHUB);
    });

    test('should detect GitHub from SSH URL', () => {
      expect(detectGitProvider('git@github.com:owner/repo.git')).toBe(GitProvider.GITHUB);
    });

    test('should detect GitHub from complex repository names', () => {
      expect(detectGitProvider('https://github.com/my-org/my-repo-name')).toBe(GitProvider.GITHUB);
    });

    test('should detect GitHub from SSH URL with complex names', () => {
      expect(detectGitProvider('git@github.com:my-org/my-repo-name.git')).toBe(GitProvider.GITHUB);
    });
  });

  describe('BitBucket URLs', () => {
    test('should detect BitBucket from HTTPS URL', () => {
      expect(detectGitProvider('https://bitbucket.org/owner/repo')).toBe(GitProvider.BIT_BUCKET);
    });

    test('should detect BitBucket from HTTPS URL with trailing slash', () => {
      expect(detectGitProvider('https://bitbucket.org/owner/repo/')).toBe(GitProvider.BIT_BUCKET);
    });

    test('should detect BitBucket from SSH URL', () => {
      expect(detectGitProvider('git@bitbucket.org:owner/repo.git')).toBe(GitProvider.BIT_BUCKET);
    });

    test('should detect BitBucket from complex repository names', () => {
      expect(detectGitProvider('https://bitbucket.org/my-org/my-repo-name')).toBe(GitProvider.BIT_BUCKET);
    });

    test('should detect BitBucket from SSH URL with complex names', () => {
      expect(detectGitProvider('git@bitbucket.org:my-org/my-repo-name.git')).toBe(GitProvider.BIT_BUCKET);
    });
  });

  describe('Invalid URLs', () => {
    test('should return null for empty string', () => {
      expect(detectGitProvider('')).toBe(null);
    });

    test('should return null for null input', () => {
      expect(detectGitProvider(null as unknown as string)).toBe(null);
    });

    test('should return null for undefined input', () => {
      expect(detectGitProvider(undefined as unknown as string)).toBe(null);
    });

    test('should return null for invalid GitHub URL format', () => {
      expect(detectGitProvider('https://github.com/owner')).toBe(null);
    });

    test('should return null for invalid BitBucket URL format', () => {
      expect(detectGitProvider('https://bitbucket.org/owner')).toBe(null);
    });

    test('should return null for non-Git URLs', () => {
      expect(detectGitProvider('https://example.com/owner/repo')).toBe(null);
    });

    test('should return null for malformed SSH URLs', () => {
      expect(detectGitProvider('git@github.com/owner/repo.git')).toBe(null);
    });

    test('should return null for GitHub URL with extra path segments', () => {
      expect(detectGitProvider('https://github.com/owner/repo/issues')).toBe(null);
    });

    test('should return null for BitBucket URL with extra path segments', () => {
      expect(detectGitProvider('https://bitbucket.org/owner/repo/src')).toBe(null);
    });

    test('should return null for random strings', () => {
      expect(detectGitProvider('not-a-url')).toBe(null);
    });

    test('should return null for other Git hosting services', () => {
      expect(detectGitProvider('https://gitlab.com/owner/repo')).toBe(null);
    });
  });

  describe('Edge cases', () => {
    test('should handle URLs with special characters in owner/repo names', () => {
      expect(detectGitProvider('https://github.com/owner-name/repo_name')).toBe(GitProvider.GITHUB);
      expect(detectGitProvider('https://bitbucket.org/owner-name/repo_name')).toBe(GitProvider.BIT_BUCKET);
    });

    test('should handle SSH URLs without .git extension', () => {
      expect(detectGitProvider('git@github.com:owner/repo')).toBe(null);
      expect(detectGitProvider('git@bitbucket.org:owner/repo')).toBe(null);
    });

    test('should be case sensitive for domain names', () => {
      expect(detectGitProvider('https://GitHub.com/owner/repo')).toBe(null);
      expect(detectGitProvider('https://BitBucket.org/owner/repo')).toBe(null);
    });

    test('should not match subdomains', () => {
      expect(detectGitProvider('https://api.github.com/owner/repo')).toBe(null);
      expect(detectGitProvider('https://api.bitbucket.org/owner/repo')).toBe(null);
    });

    test('should handle numeric owner and repo names', () => {
      expect(detectGitProvider('https://github.com/123/456')).toBe(GitProvider.GITHUB);
      expect(detectGitProvider('https://bitbucket.org/123/456')).toBe(GitProvider.BIT_BUCKET);
    });
  });
});