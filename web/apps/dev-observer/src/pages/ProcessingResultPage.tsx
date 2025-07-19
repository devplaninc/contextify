import {useParams} from "react-router";
import {useProcessingResult} from "@/components/processing/use-processing.tsx";
import {ErrorAlert} from "@/components/ErrorAlert.tsx";
import {Loader} from "@/components/Loader.tsx";
import {ProcessingResultView} from "@/components/processing/ProcessingResult.tsx";

export function ProcessingResultPage() {
  const { id } = useParams<{ id: string }>();
  const {result, loading, error} = useProcessingResult(id!)
  if (!result) {
    if (error) {
      return <ErrorAlert err={error} />
    }
    if (loading) {
      return <Loader />
    }
    return <div>No result found</div>
  }
  return <ProcessingResultView result={result} />
}