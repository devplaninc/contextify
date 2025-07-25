import {Button} from "../ui/button";
import {useCallback, useState} from "react";
import {processingItemsAPI} from "@/store/apiPaths.tsx";
import {fetchWithAuth} from "@/store/api.tsx";
import {CreateProcessingItemRequest, CreateProcessingItemResponse} from "@devplan/observer-api";
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
import {MultiRepositorySelector} from "@/components/repos/RepositorySelector.tsx";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select.tsx";
import {TimezoneSelector, getCurrentTimezone, getTimezoneAbbreviation} from "@/components/ui/timezone-selector.tsx";

export interface RequestAggregatedSummaryButtonProps {
  gitRepoIds?: string[]
}

export function RequestAggregatedSummaryButton(props: RequestAggregatedSummaryButtonProps) {
  const {gitRepoIds: initialGitRepoIds} = props;
  const [running, setRunning] = useState(false)
  const [open, setOpen] = useState(false)
  const [namespace, setNamespace] = useState<string>("")
  const [createdBy, setCreatedBy] = useState<string>("")
  const [lookBackDays, setLookBackDays] = useState(7)
  const [id, setId] = useState<string>("")
  const [referenceId, setReferenceId] = useState<string>("")
  const [endDate, setEndDate] = useState<string>(new Date().toISOString().split('T')[0])
  const [selectedRepoIds, setSelectedRepoIds] = useState<string[]>(initialGitRepoIds ?? [])

  // Schedule configuration state
  const [scheduleType, setScheduleType] = useState<"daily" | "weekly">("daily")
  const [scheduleHour, setScheduleHour] = useState(7) // 7am default
  const [scheduleMinute, setScheduleMinute] = useState(0)
  const [scheduleDayOfWeek, setScheduleDayOfWeek] = useState<number>(1) // 1 = Monday
  const [selectedTimezone, setSelectedTimezone] = useState<string>(getCurrentTimezone())

  const generate = useCallback(() => {
    if (selectedRepoIds.length === 0) {
      toast.error("Please select at least one repository")
      return
    }
    setRunning(true)
    fetchWithAuth(processingItemsAPI(), CreateProcessingItemResponse, {
      method: "POST", body: JSON.stringify(CreateProcessingItemRequest.toJSON({
        key: {entity: {$case: "periodicAggregationId", value: id}},
        data: {
          createdBy,
          namespace,
          referenceId,
          type: {
            $case: "periodicAggregation", value: {
              params: {
                lookBackDays,
                endDate: new Date(endDate),
                target: {
                  gitRepoIds: selectedRepoIds
                }
              },
              schedule: {
                frequency: scheduleType === "daily" ? {
                  type: {
                    $case: "daily",
                    value: {
                      time: {
                        timeOfDay: {
                          hours: scheduleHour,
                          minutes: scheduleMinute,
                        },
                        timeZone: {
                          id: selectedTimezone
                        }
                      }
                    }
                  }
                } : {
                  type: {
                    $case: "weekly",
                    value: {
                      dayOfWeek: scheduleDayOfWeek,
                      time: {
                        timeOfDay: {
                          hours: scheduleHour,
                          minutes: scheduleMinute,
                        },
                        timeZone: {
                          id: selectedTimezone
                        }
                      }
                    }
                  }
                }
              }
            }
          },
        },
        processImmediately: true,
      }))
    }).then(() => {
      toast.success(`New aggregated summary submitted`)
      setOpen(false)
    })
      .catch((e: unknown) => {
        toast.error(`Failed to generate aggregated summary request: ${String(e)}`)
      })
      .finally(() => setRunning(false))
  }, [selectedRepoIds, id, createdBy, namespace, referenceId, lookBackDays, endDate, scheduleType, scheduleHour, scheduleMinute, scheduleDayOfWeek, selectedTimezone])

  return <Dialog open={open} onOpenChange={setOpen}>
    <DialogTrigger asChild>
      <Button>New Aggregated Summary</Button>
    </DialogTrigger>
    <DialogContent>
      <DialogTitle>Request a new aggregated summary</DialogTitle>
      <DialogDescription>
        Provide request parameters for aggregated summary across multiple repositories
      </DialogDescription>
      <div className="text-sm">
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <div className="w-[120px]">ID</div>
            <Input onChange={e => setId(e.target.value)} value={id} className="w-[200px]"/>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-[120px]">Reference ID</div>
            <Input onChange={e => setReferenceId(e.target.value)} value={referenceId} className="w-[200px]"/>
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
          <div className="flex items-center gap-2">
            <div className="w-[120px]">First report end date</div>
            <Input
              type="date"
              onChange={e => setEndDate(e.target.value)}
              value={endDate}
              className="w-[200px]"
            />
          </div>
          <div className="flex items-center gap-2">
            <div className="w-[120px]">Repositories</div>
            <MultiRepositorySelector
              value={selectedRepoIds}
              onValueChange={setSelectedRepoIds}
              className="w-[200px]"
              placeholder="Select repositories..."
            />
          </div>
          <div className="flex items-center gap-2">
            <div className="w-[120px]">Schedule Type</div>
            <Select value={scheduleType} onValueChange={(value: "daily" | "weekly") => setScheduleType(value)}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Select schedule type..." />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="daily">Daily</SelectItem>
                <SelectItem value="weekly">Weekly</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-[120px]">Schedule Time</div>
            <div className="flex gap-2">
              <Input
                type="number"
                min="0"
                max="23"
                onChange={e => setScheduleHour(Number(e.target.value))}
                value={scheduleHour}
                className="w-[80px]"
                placeholder="Hour"
              />
              <span className="self-center">:</span>
              <Input
                type="number"
                min="0"
                max="59"
                onChange={e => setScheduleMinute(Number(e.target.value))}
                value={scheduleMinute}
                className="w-[80px]"
                placeholder="Min"
              />
              <span className="self-center text-xs text-muted-foreground">{getTimezoneAbbreviation(selectedTimezone)}</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-[120px]">Timezone</div>
            <TimezoneSelector
              value={selectedTimezone}
              onValueChange={setSelectedTimezone}
              className="w-[200px]"
              placeholder="Select timezone..."
            />
          </div>
          {scheduleType === "weekly" && (
            <div className="flex items-center gap-2">
              <div className="w-[120px]">Day of Week</div>
              <Select value={scheduleDayOfWeek.toString()} onValueChange={(value) => setScheduleDayOfWeek(Number(value))}>
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder="Select day..." />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">Monday</SelectItem>
                  <SelectItem value="2">Tuesday</SelectItem>
                  <SelectItem value="3">Wednesday</SelectItem>
                  <SelectItem value="4">Thursday</SelectItem>
                  <SelectItem value="5">Friday</SelectItem>
                  <SelectItem value="6">Saturday</SelectItem>
                  <SelectItem value="7">Sunday</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}
        </div>
      </div>
      <DialogFooter>
        <Button onClick={generate} disabled={running}>
          {running && <Loader/>}Request Aggregated Summary
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
}