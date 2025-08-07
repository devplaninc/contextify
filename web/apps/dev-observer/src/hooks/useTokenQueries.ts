import {useQuery} from '@tanstack/react-query';
import {useCallback} from "react";
import {useShallow} from "zustand/react/shallow";
import {useBoundStore} from "@/store/use-bound-store.tsx";
import type {QueryResultCommon} from "@/hooks/queries.tsx";
import type {RepoToken} from "@devplan/contextify-api";

// Query keys for caching and invalidation
export const tokenKeys = {
  all: ['tokens'] as const,
  lists: () => [...tokenKeys.all, 'list'] as const,
  namespaced: (namespace?: string) => [...tokenKeys.all, 'namespace', namespace ?? "__all__"] as const,
  detail: (id: string) => [...tokenKeys.all, 'detail', id] as const,
  filtered: (provider?: number, workspace?: string, repo?: string) =>
    [...tokenKeys.all, 'filtered', provider, workspace, repo] as const,
};

export interface AddTokenRequest {
  namespace: string;
  provider: number;
  workspace?: string;
  repo?: string;
  system: boolean;
  token: string;
  expiresAtMs?: number;
}

export interface UpdateTokenRequest {
  token: string;
}

// Hook for fetching tokens with optional filters
export function useTokens(namespace?: string): { tokens: RepoToken[] | undefined } & QueryResultCommon {
  const {listTokens} = useBoundStore();
  const queryFn = useCallback(async () => {
    return await listTokens({namespace})
  }, [listTokens, namespace]);

  const {data: ids, isFetching, error, refetch} = useQuery({
    queryKey: tokenKeys.namespaced(namespace),
    queryFn
  });

  const tokens = useBoundStore(useShallow(
    s => ids ? ids.map(id => s.tokens?.[id]).filter(v => v !== undefined) : undefined));

  return {
    tokens,
    loading: isFetching,
    error: error,
    reload: async () => {
      await refetch();
    }
  };
}

