import {useBoundStore} from "@/store/use-bound-store.tsx";
import {useCallback} from "react";
import {useQuery} from "@tanstack/react-query";
import {useShallow} from "zustand/react/shallow";
import {ProcessingItemResult, ProcessingItemsFilter, ProcessingResultFilter} from "@devplan/contextify-api";

export const processingKeys = {
  all: ['processing'] as const,
  filteredItems: (filter: ProcessingItemsFilter) => [
    ...processingKeys.all, 'items', 'filter', JSON.stringify(ProcessingItemsFilter.toJSON(filter)),
  ] as const,
  filteredResult: (filter: ProcessingResultFilter, from: Date, to: Date) => [
    ...processingKeys.all, 'results', 'filter', JSON.stringify(ProcessingResultFilter.toJSON(filter)), from, to
  ] as const,
  result: (id: string) => [...processingKeys.all, 'results', 'detail', id] as const,
};

export function useProcessingItems(filter: ProcessingItemsFilter) {
  const {fetchProcessingItems} = useBoundStore();
  const queryFn = useCallback(
    async () => fetchProcessingItems(filter), [filter, fetchProcessingItems])
  const {data: ids, isFetching, error, refetch} = useQuery({
    queryKey: processingKeys.filteredItems(filter),
    queryFn
  });
  const items = useBoundStore(useShallow(s => ids?.map(i => s.processingItems[i]).filter(v => v !== undefined)));
  return {
    items,
    loading: isFetching,
    error: error,
    reload: async () => {
      await refetch()
    }
  }
}

export function useProcessingResultsForNamespace(from: Date, to: Date, filter: ProcessingResultFilter) {
  const {fetchProcessingItemResults} = useBoundStore();
  const queryFn = useCallback(async () => fetchProcessingItemResults({
    filter: filter,
    fromDate: from,
    toDate: to
  }), [filter, from, to, fetchProcessingItemResults])
  const {data: ids, isFetching, error, refetch} = useQuery({
    queryKey: processingKeys.filteredResult(filter, from, to),
    queryFn
  });
  const results = useBoundStore(useShallow(s => ids?.map(i => s.processingResults[i]).filter(v => v !== undefined)));
  return {
    results,
    loading: isFetching,
    error: error,
    reload: async () => {
      await refetch()
    }
  }
}

export function useProcessingResult(id: string) {
  const {fetchProcessingItemResult} = useBoundStore();
  const queryFn = useCallback(
    async () => {
      await fetchProcessingItemResult(id)
      return true
    }, [fetchProcessingItemResult, id])
  const {isFetching, error, refetch} = useQuery({
    queryKey: processingKeys.result(id),
    queryFn
  });
  const result: ProcessingItemResult | undefined = useBoundStore(useShallow(s => s.processingResults[id]));
  return {
    result,
    loading: isFetching,
    error: error,
    reload: async () => {
      await refetch()
    }
  }
}