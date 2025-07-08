import {Button} from "../ui/button";
import {useCallback, useState} from "react";
import {processingRequestRunsAPI} from "@/store/apiPaths.tsx";
import {fetchWithAuth} from "@/store/api.tsx";
import {RunProcessingRequest, RunProcessingResponse} from "@devplan/observer-api";
import {v4 as uuid} from "uuid";
import {Loader} from "@/components/Loader.tsx";
import {toast} from "sonner";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogTitle,
  DialogTrigger
} from "@/components/ui/dialog.tsx";
import {Input} from "@/components/ui/input.tsx";

export interface RequestRepoChangesSummaryButtonProps {
  gitRepoId: string
}

export function RequestRepoChangesSummaryButton(props: RequestRepoChangesSummaryButtonProps) {
  const {gitRepoId} = props;
  const [running, setRunning] = useState(false)
  const [open, setOpen] = useState(false)
  const [namespace, setNamespace] = useState<string>("")
  const [createdBy, setCreatedBy] = useState<string>("")
  const [lookBackDays, setLookBackDays] = useState(7)
  const generate = useCallback(() => {
    setRunning(true)
    fetchWithAuth(processingRequestRunsAPI(), RunProcessingResponse, {
      method: "POST", body: JSON.stringify(RunProcessingRequest.toJSON({
        requestId: uuid(),
        request: {
          type: {$case: "gitChanges", value: {gitRepoId, lookBackDays}},
          createdBy,
          namespace,
          referenceId: gitRepoId,
        }
      }))
    }).then(() => {
      toast.success(`New analysis submitted`)
      setOpen(false)
    })
      .catch(e => {
        toast.error(`Failed to generate processing request: ${e}`)
      })
      .finally(() => setRunning(false))
  }, [createdBy, gitRepoId, lookBackDays, namespace])
  return <Dialog open={open} onOpenChange={setOpen}>
    <DialogTrigger asChild>
      <Button>New Report</Button>
    </DialogTrigger>
    <DialogContent>
      <DialogTitle>Request a new git changes report</DialogTitle>
      <DialogDescription>
        Provide request parameters
      </DialogDescription>
      <div className="text-sm">
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <div className="w-[120px]">Namespace</div>
            <Input onChange={e => setNamespace(e.target.value)} value={namespace} className="w-[200px]"/>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-[120px]">Created by</div>
            <Input onChange={e => setCreatedBy(e.target.value)} value={createdBy} className="w-[200px]"/>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-[10px]">Look Back Days</div>
            <Input onChange={e => setLookBackDays(Number(e.target.value))} value={lookBackDays} className="w-[200px]"/>
          </div>
        </div>
      </div>
      <DialogFooter>
        <Button onClick={generate} disabled={running}>
          {running && <Loader/>}Request
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
}