import { GitProvider } from '../pb/dev_observer/api/types/repo';

// Detect Git provider from URL
export const detectGitProvider = (url: string): GitProvider | null => {
  if (!url) return null;
  
  // GitHub patterns
  const githubHttpPattern = /^https:\/\/github\.com\/[^\\/]+\/[^\\/]+\/?$/;
  const githubSshPattern = /^git@github\.com:[^\\/]+\/[^\\/]+\.git$/;
  if (githubHttpPattern.test(url) || githubSshPattern.test(url)) {
    return GitProvider.GITHUB;
  }
  
  // BitBucket patterns
  const bitbucketHttpPattern = /^https:\/\/bitbucket\.org\/[^\\/]+\/[^\\/]+\/?$/;
  const bitbucketSshPattern = /^git@bitbucket\.org:[^\\/]+\/[^\\/]+\.git$/;
  if (bitbucketHttpPattern.test(url) || bitbucketSshPattern.test(url)) {
    return GitProvider.BIT_BUCKET;
  }
  
  return null;
};