import type {ValidationError} from "@/types/repository.ts";
import type {GitHubRepository} from "@devplan/contextify-api";

// Validate GitHub repository URL
export const validateGitHubUrl = (url: string, repos: Record<string, GitHubRepository>): ValidationError | null => {
  if (!url) {
    return {field: "url", message: "Repository URL is required"};
  }

  // Check if it's a GitHub URL
  const githubHttpPattern = /^https:\/\/github\.com\/[^\\/]+\/[^\\/]+\/?$/;
  const githubSshPattern = /^git@github\.com:[^\\/]+\/[^\\/]+\.git$/;

  if (!githubHttpPattern.test(url) && !githubSshPattern.test(url)) {
    return {
      field: "url",
      message: "URL must be a valid GitHub repository URL",
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

// Extract repository name from URL
export const extractRepoName = (url: string): string => {
  try {
    if (url.startsWith("https://github.com/")) {
      // Handle HTTPS URL
      const parts = url.replace("https://github.com/", "").split("/");
      return parts.slice(0, 2).join("/");
    } else if (url.startsWith("git@github.com:")) {
      // Handle SSH URL
      const parts = url.replace("git@github.com:", "").replace(".git", "").split("/");
      return parts.join("/");
    }
  } catch (error) {
    console.error("Error extracting repo name:", error);
  }
  return "Unknown Repository";
};

// Simulate network latency
export const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));