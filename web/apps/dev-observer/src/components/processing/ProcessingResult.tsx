import type {ProcessGitChangesRequest, ProcessingItemResult, ProcessingRequest} from "@devplan/contextify-api";
import {AnalysisContents} from "@/components/analysis/AnalysisList.tsx";
import {Badge} from "@/components/ui/badge.tsx";

export function ProcessingResultView({result}: { result: ProcessingItemResult }) {
  return <div className="space-x-4">
    <div className="text-sm font-semibold">
      <ProcessingResultHeader result={result}/>
    </div>
    <AnalysisContents keys={result.observations}/>
  </div>
}

export function ProcessingResultHeader({result}: { result: ProcessingItemResult }) {
  return <div className="flex items-center gap-2">
    <Badge>{result.createdAt?.toLocaleString()}</Badge>
    <ResultSpecificHeader result={result}/>
  </div>
}

function ResultSpecificHeader({result}: { result: ProcessingItemResult }) {
  if (result.data?.type?.$case === "request") {
    return <RequestHeader result={result} request={result.data.type.value}/>
  }
  return null
}

function RequestHeader(params: { result: ProcessingItemResult, request: ProcessingRequest }) {
  const {result} = params
  return <div className="flex items-center gap-2">
    <RequestTypeHeader {...params} />
    {result.data?.namespace && <div>ns: {result.data?.namespace}</div>}
    {result.data?.createdBy && <div>createdBy: {result.data?.createdBy}</div>}
  </div>
}

function RequestTypeHeader({request, result}: { request: ProcessingRequest, result: ProcessingItemResult }) {
  switch (request.type?.$case) {
    case "gitChanges":
      return <GitChangesHeader result={result} info={request.type.value}/>
  }
  return null
}

function GitChangesHeader({result, info}: { result: ProcessingItemResult, info: ProcessGitChangesRequest }) {
  const fromDate = new Date(result.createdAt!.getTime() - (info.lookBackDays * 24 * 60 * 60 * 1000));
  return <div className="flex gap-2">
    <div>Git Changes Analysis:</div>
    <div>{fromDate.toLocaleDateString()}</div>
    <div>-</div>
    <div>{result.createdAt!.toLocaleDateString()}</div>
  </div>
}