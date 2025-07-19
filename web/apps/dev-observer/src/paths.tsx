export function processingResultPath<I extends string>(id: I) {
  return `/processing/results/${id}` as const;
}