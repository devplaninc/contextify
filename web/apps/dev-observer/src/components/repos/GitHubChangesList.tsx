import type {GitHubRepository} from "@devplan/observer-api";
import {useBoundStore} from "@/store/use-bound-store.tsx";
import {useShallow} from "zustand/react/shallow";
import {Loader} from "@/components/Loader.tsx";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Accordion, AccordionContent, AccordionItem, AccordionTrigger} from "@/components/ui/accordion.tsx";
import {Markdown} from "@/components/text/Markdown.tsx";
import {useObservation} from "@/hooks/useObservationQueries.ts";
import {ErrorAlert} from "@/components/ErrorAlert.tsx";
import {Button} from "@/components/ui/button.tsx";
import {RefreshCw} from "lucide-react";
import {useState} from "react";

export function GitHubChangesList({repo}: { repo: GitHubRepository }) {
  const [isTriggering, setIsTriggering] = useState(false);
  
  const keys = useBoundStore(useShallow(s => {
    return s.observationKeys["github_changes"]?.filter(k => k.key.startsWith(repo.fullName))
  }))

  const triggerAnalysis = async () => {
    setIsTriggering(true);
    try {
      const response = await fetch(`/api/github-changes/${repo.id}/trigger`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error('Failed to trigger analysis');
      }
      // Optionally refresh the data or show a success message
    } catch (error) {
      console.error('Failed to trigger analysis:', error);
    } finally {
      setIsTriggering(false);
    }
  };

  if (keys === undefined) {
    return <Loader/>
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>GitHub Changes Summary</CardTitle>
          <Button 
            onClick={triggerAnalysis} 
            disabled={isTriggering}
            size="sm"
            variant="outline"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isTriggering ? 'animate-spin' : ''}`} />
            {isTriggering ? 'Analyzing...' : 'Refresh Analysis'}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {keys.length === 0 ? (
          <div className="bg-muted p-8 rounded-lg text-center">
            <h3 className="text-xl font-medium mb-2">No changes analysis available</h3>
            <p className="text-muted-foreground mb-4">
              Click "Refresh Analysis" to analyze recent changes in this repository.
            </p>
          </div>
        ) : (
          <Accordion type="multiple" className="w-full">
            {keys.map(key => (
              <AccordionItem value={key.name} key={key.key}>
                <AccordionTrigger className="text-sm font-medium justify-start">
                  <div className="flex items-center gap-2">
                    <span>{getDisplayName(key.name, key.key)}</span>
                    <span className="text-xs text-muted-foreground">
                      ({getPeriodFromKey(key.key)})
                    </span>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="pl-4">
                  <GitHubChangesContent observationKey={key}/>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        )}
      </CardContent>
    </Card>
  );
}

function GitHubChangesContent({observationKey}: { observationKey: any }) {
  const {observation, error} = useObservation(observationKey)
  
  if (!observation) {
    if (error) {
      return <ErrorAlert err={error}/>
    }
    return <Loader/>
  }
  
  return (
    <div className="space-y-4">
      <Markdown content={observation.content}/>
    </div>
  );
}

function getDisplayName(name: string, key: string): string {
  // Extract meaningful display name from the key
  if (name === "changes_summary") {
    return "Recent Changes Summary";
  }
  return name;
}

function getPeriodFromKey(key: string): string {
  // Extract period from key like "owner/repo/changes_7d"
  const parts = key.split('/');
  const lastPart = parts[parts.length - 1];
  if (lastPart.startsWith('changes_') && lastPart.endsWith('d')) {
    const days = lastPart.replace('changes_', '').replace('d', '');
    return `Last ${days} days`;
  }
  return "Recent";
}