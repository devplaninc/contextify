import type {ValidationError} from "@/types/repository.ts";
import type {GitRepository} from "@devplan/contextify-api";
import {GitProvider} from "@devplan/contextify-api";

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

// Validate repository URL for supported Git providers
export const validateRepositoryUrl = (url: string, repos: Record<string, GitRepository>): ValidationError | null => {
  if (!url) {
    return {field: "url", message: "Repository URL is required"};
  }

  // Auto-detect the provider from the URL
  const provider = detectGitProvider(url);
  
  if (!provider) {
    return {
      field: "url",
      message: "URL must be a valid GitHub or BitBucket repository URL",
    };
  }

  // Check for duplicates
  const isDuplicate = Object.values(repos).some((repo) => repo.url === url);
  if (isDuplicate) {
    return {
      field: "url",
      message: "This repository has already been added",
    };
  }

  return null;
};


// Extract repository name from URL for supported Git providers
export const extractRepoName = (url: string): string => {
  try {
    // GitHub URLs
    if (url.startsWith("https://github.com/")) {
      const parts = url.replace("https://github.com/", "").split("/");
      return parts.slice(0, 2).join("/");
    } else if (url.startsWith("git@github.com:")) {
      const parts = url.replace("git@github.com:", "").replace(".git", "").split("/");
      return parts.join("/");
    }
    // BitBucket URLs
    else if (url.startsWith("https://bitbucket.org/")) {
      const parts = url.replace("https://bitbucket.org/", "").split("/");
      return parts.slice(0, 2).join("/");
    } else if (url.startsWith("git@bitbucket.org:")) {
      const parts = url.replace("git@bitbucket.org:", "").replace(".git", "").split("/");
      return parts.join("/");
    }
  } catch (error) {
    console.error("Error extracting repo name:", error);
  }
  return "Unknown Repository";
};
