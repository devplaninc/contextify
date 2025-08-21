export const ownDomain = import.meta.env.VITE_KEEP_OWN_DOMAIN !== undefined ? "" : "http://localhost:8090";

export function baseAPI() {
  return `${ownDomain}/api/v1` as const;
}

export function configAPI() {
  return `${baseAPI()}/config` as const;
}

export function usersStatusAPI() {
  return `${configAPI()}/users/status` as const;
}

export function reposAPI() {
  return `${baseAPI()}/repositories` as const;
}

export function repoAPI<R extends string>(repoId: R) {
  return `${reposAPI()}/${repoId}` as const;
}

export function repoRescanAPI<R extends string>(repoId: R) {
  return `${repoAPI(repoId)}/rescan` as const;
}

export function repoBackfillSummariesAPI() {
  return `${reposAPI()}/actions/backfill-summaries` as const;
}

export function observationsAPI<K extends string>(kind: K) {
  return `${baseAPI()}/observations/kind/${kind}` as const;
}

export function observationAPI<K extends string, N extends string, C extends string>(kind: K, name: N, key: C) {
  return `${baseAPI()}/observation/${kind}/${encodeURIComponent(name)}/${enc(key)}` as const;
}

export function processingItemsAPI() {
  return `${baseAPI()}/processing/items` as const;
}

export function processingItemsFilterAPI() {
  return `${processingItemsAPI()}/filter` as const;
}

export function processingResultsAPI() {
  return `${baseAPI()}/processing/results` as const;
}

export function processingResultAPI<I extends string>(id: I) {
  return `${processingResultsAPI()}/${id}` as const;
}

export function processingRequestsAPI() {
  return `${baseAPI()}/processing/requests` as const;
}

export function processingRequestRunsAPI() {
  return `${processingRequestsAPI()}/runs` as const;
}

export function processingRequestRunAPI<R extends string>(requestId: R) {
  return `${processingRequestRunsAPI()}/${requestId}` as const;
}

export function tokensAPI() {
  return `${baseAPI()}/tokens`;
}
export function tokensListAPI() {
  return `${tokensAPI()}/list`;
}
export function tokenAPI<T extends string>(id: T) {
  return `${tokensAPI()}/token/${id}`
}

// Encodes as base64
function enc(v: string): string {
  // TODO: perform safe encoding
  return v.replace(/\//g, '|');
}
