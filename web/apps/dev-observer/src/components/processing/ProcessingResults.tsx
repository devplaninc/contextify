import {useProcessingResultsForNamespace} from "@/components/processing/use-processing.tsx";
import {ErrorAlert} from "@/components/ErrorAlert.tsx";
import {Loader} from "@/components/Loader.tsx";
import type {ProcessingItemResult, ProcessingResultFilter} from "@devplan/observer-api";
import {Link} from "react-router";
import {processingResultPath} from "@/paths.tsx";
import {ProcessingResultHeader} from "@/components/processing/ProcessingResult.tsx";
import {useState} from "react";
import {DateTimePicker} from "@/components/common/DateTimePicker.tsx";
import {Button} from "@/components/ui/button.tsx";
import {useForm} from "react-hook-form";
import {zodResolver} from "@hookform/resolvers/zod";
import {z} from "zod";
import {Form, FormControl, FormField, FormItem, FormLabel, FormMessage,} from "@/components/ui/form.tsx";
import {Input} from "@/components/ui/input.tsx";
import {toast} from "sonner";

const formSchema = z.object({
  namespace: z.string().optional(),
  from: z.date({required_error: "From date is required"}),
  to: z.date({required_error: "To date is required"}),
}).refine((data) => data.from <= data.to, {
  message: "From date must be before or equal to To date",
  path: ["to"],
});

type formValues = z.infer<typeof formSchema>;

export interface ProcessingResultsProps {
  referenceId: string
}

export function ProcessingResults({referenceId}: ProcessingResultsProps) {
  const [filter, setFilter] = useState<ProcessingResultFilter>({referenceId});
  const [dates, setDates] = useState({
    from: new Date(new Date().getTime() - 7 * 24 * 60 * 60 * 1000),
    to: new Date(),
  });

  // Form setup
  const form = useForm<formValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {...dates},
  });

  const setAppliedValues = (values: formValues) => {
    setFilter({...filter, ...values})
    setDates({...dates, ...values})
    toast.success("Filter applied")
    console.log("setAppliedValues", {values})
  }

  return <div className="space-y-4">
    <div className="border-b pb-2 space-y-2">
      <div className="font-semibold text-lg">Reports Filter:</div>
      <Form {...form}>
        {/* eslint-disable-next-line @typescript-eslint/no-misused-promises */}
        <form onSubmit={form.handleSubmit(setAppliedValues)} className="flex items-center gap-4">
          <FormField control={form.control} name="namespace" render={({field}) => (
            <FormItem className="flex items-center gap-2">
              <FormLabel>Namespace:</FormLabel>
              <FormControl><Input {...field}/></FormControl>
              <FormMessage/>
            </FormItem>
          )}/>

          <FormField control={form.control} name="from" render={({field}) => (
            <FormItem className="flex items-center gap-2">
              <FormLabel>From:</FormLabel>
              <FormControl><DateTimePicker onSelect={field.onChange} initial={field.value}/></FormControl>
              <FormMessage/>
            </FormItem>
          )}/>

          <FormField control={form.control} name="to" render={({field}) => (
            <FormItem className="flex items-center gap-2">
              <FormLabel>To:</FormLabel>
              <FormControl><DateTimePicker onSelect={field.onChange} initial={field.value}/></FormControl>
              <FormMessage/>
            </FormItem>
          )}/>


          <div>
            <Button type="submit">Apply</Button>
          </div>

        </form>
      </Form>
    </div>
    <FilteredProcessingResults filter={filter} {...dates} />
  </div>
}


export interface FilteredProcessingResultsProps {
  filter: ProcessingResultFilter
  from: Date
  to: Date
}

export function FilteredProcessingResults({filter, from, to}: FilteredProcessingResultsProps) {
  const {results, error} = useProcessingResultsForNamespace(from, to, filter)
  if (results === undefined) {
    if (error) {
      return <ErrorAlert err={error}/>
    }
    return <Loader/>
  }
  return <div className="space-y-2">
    {results.map(r => <ProcessingResultRecord key={r.id} result={r}/>)}
  </div>
}

function ProcessingResultRecord({result}: { result: ProcessingItemResult }) {
  return <div
    className="flex items-center gap-2 border rounded-md shadow text-sm font-medium p-4 hover:bg-muted transition-colors">
    <Link to={processingResultPath(result.id)}>
      <ProcessingResultHeader result={result}/>
    </Link>
  </div>
}
