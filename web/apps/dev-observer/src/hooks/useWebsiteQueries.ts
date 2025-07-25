import {useQuery} from '@tanstack/react-query';
import {useCallback} from "react";
import {useShallow} from "zustand/react/shallow";
import {useBoundStore} from "@/store/use-bound-store.tsx";
import type {QueryResultCommon} from "@/hooks/queries.tsx";
import type {WebSite} from "@devplan/contextify-api";

// Query keys for caching and invalidation
export const websiteKeys = {
  all: ['websites'] as const,
  lists: () => [...websiteKeys.all, 'list'] as const,
  detail: (id: string) => [...websiteKeys.all, 'detail', id] as const,
};

export function useWebsites(): { websites: WebSite[] | undefined } & QueryResultCommon {
  const {fetchWebSites} = useBoundStore();
  const queryFn = useCallback(async () => fetchWebSites().then(() => true), [fetchWebSites])
  const {isFetching, error, refetch} = useQuery({queryKey: websiteKeys.lists(), queryFn});
  const websites = useBoundStore(useShallow(s => Object.values(s.websites)));
  return {
    websites, loading: isFetching, error: error,
    reload: async () => {
      await refetch()
    }
  }
}

export function useWebsite(id: string): { website: WebSite | undefined } & QueryResultCommon {
  const {fetchWebSite} = useBoundStore();
  const queryFn = useCallback(async () => fetchWebSite(id).then(() => true), [fetchWebSite, id])
  const {error, isFetching: loading, refetch} = useQuery({queryKey: websiteKeys.detail(id), queryFn, enabled: !!id});
  const website = useBoundStore(useShallow(s => s.websites[id]));
  return {
    website, loading, error, reload: async () => {
      await refetch()
    }
  }
}
