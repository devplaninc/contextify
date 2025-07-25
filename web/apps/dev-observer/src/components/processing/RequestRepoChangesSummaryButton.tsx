import {Button} from "../ui/button";
import {useCallback, useState} from "react";
import {processingItemsAPI} from "@/store/apiPaths.tsx";
import {fetchWithAuth} from "@/store/api.tsx";
import {CreateProcessingItemRequest, CreateProcessingItemResponse} from "@devplan/observer-api";
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
import {RepositorySelector} from "@/components/repos/RepositorySelector.tsx";

export interface RequestRepoChangesSummaryButtonProps {
  gitRepoId?: string
}

export function RequestRepoChangesSummaryButton(props: RequestRepoChangesSummaryButtonProps) {
  const {gitRepoId: initialGitRepoId} = props;
  const [running, setRunning] = useState(false)
  const [open, setOpen] = useState(false)
  const [namespace, setNamespace] = useState<string>("")
  const [createdBy, setCreatedBy] = useState<string>("")
  const [lookBackDays, setLookBackDays] = useState(7)
  const [selectedRepoId, setSelectedRepoId] = useState<string>(initialGitRepoId ?? "")
  const generate = useCallback(() => {
    if (!selectedRepoId) {
      toast.error("Please select a repository")
      return
    }
    setRunning(true)
    fetchWithAuth(processingItemsAPI(), CreateProcessingItemResponse, {
      method: "POST", body: JSON.stringify(CreateProcessingItemRequest.toJSON({
        key: {entity: {$case: "requestId", value: uuid()}},
        data: {
          createdBy,
          namespace,
          referenceId: selectedRepoId,
          type: {
            $case: "request", value: {
              type: {$case: "gitChanges", value: {gitRepoId: selectedRepoId, lookBackDays}},
            }
          },
        },
        processImmediately: true,
      }))
    }).then(() => {
      toast.success(`New analysis submitted`)
      setOpen(false)
    })
      .catch((e: unknown) => {
        toast.error(`Failed to generate processing request: ${String(e)}`)
      })
      .finally(() => setRunning(false))
  }, [createdBy, selectedRepoId, lookBackDays, namespace])
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
            <div className="w-[120px]">Repository</div>
            {!initialGitRepoId && <RepositorySelector
              value={selectedRepoId} 
              onValueChange={setSelectedRepoId}
              className="w-[200px]"
              placeholder="Select repository..."
            />}
          </div>
          <div className="flex items-center gap-2">
            <div className="w-[120px]">Namespace</div>
            <Input onChange={e => setNamespace(e.target.value)} value={namespace} className="w-[200px]"/>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-[120px]">Created by</div>
            <Input onChange={e => setCreatedBy(e.target.value)} value={createdBy} className="w-[200px]"/>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-[120px]">Look Back Days</div>
            <Input 
              type="number"
              onChange={e => setLookBackDays(Number(e.target.value))} 
              value={lookBackDays} 
              className="w-[200px]"
            />
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