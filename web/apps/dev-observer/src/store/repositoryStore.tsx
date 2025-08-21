import type {StateCreator} from "zustand";
import {repoAPI, repoBackfillSummariesAPI, repoRescanAPI, reposAPI} from "@/store/apiPaths.tsx";
import type {GitRepository} from "@devplan/contextify-api";
import {
  AddRepositoryRequest,
  AddRepositoryResponse,
  DeleteRepositoryResponse,
  GetRepositoryResponse,
  GitProvider,
  ListRepositoriesResponse,
  RescanAnalysisSummaryRequest,
  RescanAnalysisSummaryResponse,
  RescanRepositoryRequest
} from "@devplan/contextify-api";
import {fetchWithAuth, VoidParser} from "@/store/api.tsx";
import {detectGitProvider} from "@/utils/repositoryUtils.ts";

export interface RepositoryState {
  repositories: Record<string, GitRepository>;

  fetchRepositories: () => Promise<void>;
  fetchRepositoryById: (id: string) => Promise<void>;
  addRepository: (url: string) => Promise<void>;
  deleteRepository: (id: string) => Promise<void>;
  rescanRepository: (id: string, req?: RescanRepositoryRequest) => Promise<void>;
  backfillSummaries: (req: RescanAnalysisSummaryRequest) => Promise<void>;
}

export const createRepositoriesSlice: StateCreator<
  RepositoryState,
  [],
  [],
  RepositoryState
> = ((set) => ({
  repositories: {},

  fetchRepositories: async () => fetchWithAuth(reposAPI(), ListRepositoriesResponse)
    .then(res => {
      const {repos} = res
      const repositories = repos.reduce((a, r) => ({...a, [r.id]: r}), {} as Record<string, GitRepository>)
      set(s => ({...s, repositories}))
    }),

  fetchRepositoryById: async id => fetchWithAuth(repoAPI(id), GetRepositoryResponse)
    .then(r => {
      const {repo} = r
      if (repo) {
        set(s => ({...s, repositories: {...s.repositories, [repo.id]: repo}}))
      }
    }),

  addRepository: async url => {
    const provider = detectGitProvider(url) ?? GitProvider.GITHUB;
    return fetchWithAuth(
      reposAPI(),
      AddRepositoryResponse,
      {method: "POST", body: JSON.stringify(AddRepositoryRequest.toJSON({url, provider}))},
    ).then(r => {
      const {repo} = r
      if (repo) {
        set(s => ({...s, repositories: {...s.repositories, [repo.id]: repo}}))
      }
    });
  },
  deleteRepository: async id => fetchWithAuth(repoAPI(id), DeleteRepositoryResponse, {method: "DELETE"})
    .then(r => {
      const {repos} = r
      const repositories = repos.reduce((a, r) => ({...a, [r.id]: r}), {} as Record<string, GitRepository>)
      set(s => ({...s, repositories}))
    }),
  rescanRepository: async (id, req) => fetchWithAuth(repoRescanAPI(id), new VoidParser(), {
    method: "POST", body: JSON.stringify(RescanRepositoryRequest.toJSON(req ?? {}))
  }),
  backfillSummaries: async req => fetchWithAuth(repoBackfillSummariesAPI(), RescanAnalysisSummaryResponse, {
    method: "POST", body: JSON.stringify(RescanAnalysisSummaryRequest.toJSON(req))
  }).then(() => {
    return
  }),
}));
