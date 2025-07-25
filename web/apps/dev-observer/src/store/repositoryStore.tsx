import type {StateCreator} from "zustand";
import {repoAPI, repoRescanAPI, reposAPI} from "@/store/apiPaths.tsx";
import {
  AddGithubRepositoryRequest,
  AddGithubRepositoryResponse,
  DeleteRepositoryResponse,
  GetRepositoryResponse,
  ListGithubRepositoriesResponse
} from "@devplan/contextify-api";
import type {GitHubRepository} from "@devplan/contextify-api";
import {fetchWithAuth, VoidParser} from "@/store/api.tsx";

export interface RepositoryState {
  repositories: Record<string, GitHubRepository>;

  fetchRepositories: () => Promise<void>;
  fetchRepositoryById: (id: string) => Promise<void>;
  addRepository: (url: string) => Promise<void>;
  deleteRepository: (id: string) => Promise<void>;
  rescanRepository: (id: string) => Promise<void>;
}

export const createRepositoriesSlice: StateCreator<
  RepositoryState,
  [],
  [],
  RepositoryState
> = ((set) => ({
  repositories: {},

  fetchRepositories: async () => fetchWithAuth(reposAPI(), ListGithubRepositoriesResponse)
    .then(res => {
      const {repos} = res
      const repositories = repos.reduce((a, r) => ({...a, [r.id]: r}), {} as Record<string, GitHubRepository>)
      set(s => ({...s, repositories}))
    }),

  fetchRepositoryById: async id => fetchWithAuth(repoAPI(id), GetRepositoryResponse)
    .then(r => {
      const {repo} = r
      if (repo) {
        set(s => ({...s, repositories: {...s.repositories, [repo.id]: repo}}))
      }
    }),

  addRepository: async url => fetchWithAuth(
    reposAPI(),
    AddGithubRepositoryResponse,
    {method: "POST", body: JSON.stringify(AddGithubRepositoryRequest.toJSON({url}))},
  ).then(r => {
    const {repo} = r
    if (repo) {
      set(s => ({...s, repositories: {...s.repositories, [repo.id]: repo}}))
    }
  }),
  deleteRepository: async id => fetchWithAuth(repoAPI(id), DeleteRepositoryResponse, {method: "DELETE"})
    .then(r => {
      const {repos} = r
      const repositories = repos.reduce((a, r) => ({...a, [r.id]: r}), {} as Record<string, GitHubRepository>)
      set(s => ({...s, repositories}))
    }),
  rescanRepository: async id => fetchWithAuth(repoRescanAPI(id), new VoidParser(), {method: "POST"}),
}));
