import {useProcessingItemsForNamespace} from "@/components/processing/use-processing.tsx";

export interface NamespaceProcessingItemsProps {
  namespace: string
}

export function NamespaceProcessingItems({namespace}: NamespaceProcessingItemsProps) {
  useProcessingItemsForNamespace({namespace});
  return <div>{namespace}</div>
}
