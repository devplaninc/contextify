import type {QueryResultCommon} from "@/hooks/queries.tsx";
import {useBoundStore} from "@/store/use-bound-store.tsx";
import {useCallback} from "react";
import {useQuery} from "@tanstack/react-query";
import {useShallow} from "zustand/react/shallow";
import type {Observation, ObservationKey} from "@devplan/contextify-api";
import {observationKeyStr} from "@/store/observationsStore.tsx";

export const observationKeys = {
  list: (kind: string) => ['observations', 'kind', kind] as const,
  detail: (key: ObservationKey) => ["observations", 'detail', key.kind, key.name, key.key] as const,
};

export function useObservationKeys(kind: string): { keys: ObservationKey[] | undefined } & QueryResultCommon {
  const {fetchObservations} = useBoundStore();
  const queryFn = useCallback(async () => {
    await fetchObservations(kind);
    return true
  }, [fetchObservations, kind])
  const {isFetching, error, refetch} = useQuery({queryKey: observationKeys.list(kind), queryFn});
  const keys = useBoundStore(useShallow(s => s.observationKeys[kind]));
  return {
    keys, loading: isFetching, error: error,
    reload: async () => {
      await refetch()
    }
  }
}

export function useObservation(key: ObservationKey): {
  observation: Observation | undefined | null
} & QueryResultCommon {
  const {fetchObservation} = useBoundStore();
  const queryFn = useCallback(async () => {
    await fetchObservation(key);
    return true
  }, [fetchObservation, key])
  const {data, isFetching, error, refetch} = useQuery({queryKey: observationKeys.detail(key), queryFn});
  const observation = useBoundStore(useShallow(s => s.observations[observationKeyStr(key)]));
  return {
    observation: data ? observation : undefined,
    loading: isFetching, error: error,
    reload: async () => {
      await refetch()
    }
  }
}