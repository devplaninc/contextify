import type {ObservationKey} from "@devplan/contextify-api";
import {useBoundStore} from "@/store/use-bound-store.tsx";
import {useShallow} from "zustand/react/shallow";
import {Loader} from "@/components/Loader.tsx";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Accordion, AccordionContent, AccordionItem, AccordionTrigger} from "@/components/ui/accordion.tsx";
import {Markdown} from "@/components/text/Markdown.tsx";
import {useObservation} from "@/hooks/useObservationQueries.ts";
import {ErrorAlert} from "@/components/ErrorAlert.tsx";

export interface AnalysisListProps {
  kind: string,
  keysFiler: (k: ObservationKey) => boolean
}

export function AnalysisList({kind, keysFiler}: AnalysisListProps) {
  const keys = useBoundStore(useShallow(s => {
    return s.observationKeys[kind]?.filter(keysFiler)
  }))
  if (keys === undefined) {
    return <Loader/>
  }
  if (keys.length === 0) {
    return <Card>
      <CardHeader>
        <CardTitle>Analysis Data</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="bg-muted p-8 rounded-lg text-center">
          <h3 className="text-xl font-medium mb-2">No analysis data available</h3>
        </div>
      </CardContent>
    </Card>
  }
  return <div className="space-y-4">
    <div className="font-semibold">
      Analysis Data
    </div>
    <div>
      <AnalysisContents keys={keys}/>
    </div>
  </div>
}

export function AnalysisContents({keys}: { keys: ObservationKey[] }) {
  return <Accordion type="multiple" className="w-full">
    {keys.map(key => <AccordionItem value={key.name} key={key.key}>
      <AccordionTrigger className="text-sm font-medium justify-start">
        {key.name}
      </AccordionTrigger>

      <AccordionContent className="pl-4">
        <AnalysisContent observationKey={key}/>
      </AccordionContent>
    </AccordionItem>)}

  </Accordion>
}

export function AnalysisContent({observationKey}: { observationKey: ObservationKey }) {
  const {observation, error} = useObservation(observationKey)
  if (!observation) {
    if (error) {
      return <ErrorAlert err={error}/>
    }
    return <Loader/>
  }
  return <Markdown content={observation.content}/>
}