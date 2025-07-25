export function processingPath() {
  return `/processing` as const;
}

export function processingResultPath<I extends string>(id: I) {
  return `${processingPath()}/results/${id}` as const;
}
