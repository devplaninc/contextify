import type {StateCreator} from "zustand";
import {observationAPI, observationsAPI, processingItemsFilterAPI, processingResultAPI, processingResultsAPI} from "@/store/apiPaths.tsx";
import {
  type Observation,
  type ObservationKey,
  type ProcessingItem, type ProcessingItemsFilter
} from "@devplan/observer-api"
import {
  GetObservationResponse,
  GetObservationsResponse,
  GetProcessingItemsRequest,
  GetProcessingItemsResponse,
  GetProcessingResultsRequest,
  GetProcessingResultsResponse,
  GetProcessingResultResponse,
  ProcessingItemKey,
  ProcessingItemResult,
} from "@devplan/observer-api";
import {fetchWithAuth} from "@/store/api.tsx";

export interface ObservationsState {
  observationKeys: Record<string, ObservationKey[]>;
  observations: Record<string, Observation>;

  fetchObservations: (kind: string) => Promise<void>;
  fetchObservation: (key: ObservationKey) => Promise<void>;

  processingItems: Record<string, ProcessingItem>;

  fetchProcessingItemsByNamespace: (filter: ProcessingItemsFilter) => Promise<string[]>;

  processingResults: Record<string, ProcessingItemResult>;

  fetchProcessingItemResults: (req: GetProcessingResultsRequest) => Promise<string[]>;
  fetchProcessingItemResult: (id: string) => Promise<void>;
}

export const createObservationsSlice: StateCreator<
  ObservationsState,
  [],
  [],
  ObservationsState
> = ((set, get) => ({
  observationKeys: {},
  observations: {},
  fetchObservations: async kind => fetchWithAuth(observationsAPI(kind), GetObservationsResponse)
    .then(r => set(s => ({...s, observationKeys: {...s.observationKeys, [kind]: (r.keys ?? [])}}))),
  fetchObservation: async key => fetchWithAuth(observationAPI(key.kind, key.name, key.key), GetObservationResponse)
    .then(r => {
      const k = observationKeyStr(key)
      const {observation} = r
      if (observation) {
        set(s => ({...s, observations: {...s.observations, [k]: observation}}))
      } else {
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        const {[k]: _, ...observations} = get().observations
        set(s => ({...s, observations}))
      }
    }),


  processingItems: {},
  fetchProcessingItemsByNamespace: async filter => fetchWithAuth(processingItemsFilterAPI(), GetProcessingItemsResponse, {
    method: "POST",
    body: JSON.stringify(GetProcessingItemsRequest.toJSON({filter}))
  }).then(r => {
    const processingItems = r.items.reduce((a, i) => ({...a, [processingItemKeyStr(i.key!)]: i}), {})
    set(s => ({...s, processingItems: {...s.processingItems, ...processingItems}}))
    return Object.keys(processingItems)
  }),

  processingResults: {},
  fetchProcessingItemResults: async req => fetchWithAuth(processingResultsAPI(), GetProcessingResultsResponse, {
    method: "POST",
    body: JSON.stringify(GetProcessingResultsRequest.toJSON({...req}))
  }).then(r => {
    const processingResults = r.results.reduce((a, i) => ({...a, [i.id]: i}), {})
    set(s => ({...s, processingResults: {...s.processingResults, ...processingResults}}))
    return Object.keys(processingResults)
  }),
  fetchProcessingItemResult: async id => fetchWithAuth(processingResultAPI(id), GetProcessingResultResponse).then(r => {
    const {result} = r
    if (result) {
      set(s => ({...s, processingResults: {...s.processingResults, [result.id]: result}}))
    }
  })
}))

export function observationKeyStr(k: ObservationKey) {
  return `${k.kind}__${k.name}__${k.key}`
}

export function processingItemKeyStr(k: ProcessingItemKey) {
  return JSON.stringify(ProcessingItemKey.toJSON(k))
}