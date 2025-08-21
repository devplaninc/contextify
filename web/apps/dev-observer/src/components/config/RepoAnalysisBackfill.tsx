import {useCallback, useState} from "react";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Button} from "@/components/ui/button.tsx";
import {useBoundStore} from "@/store/use-bound-store.tsx";
import {toast} from "sonner";
import {Loader} from "@/components/Loader.tsx";
import {Checkbox} from "@/components/ui/checkbox.tsx";

export function RepoAnalysisBackfill() {
  const {backfillSummaries} = useBoundStore();
  const [isBackfilling, setIsBackfilling] = useState(false);
  const [force, setForce] = useState(false);

  const handleBackfill = useCallback(async () => {
    setIsBackfilling(true);
    try {
      await backfillSummaries({force});
      toast.success("Repository analysis summary backfill completed successfully");
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      toast.error(`Failed to backfill summaries: ${errorMessage}`);
    } finally {
      setIsBackfilling(false);
    }
  }, [backfillSummaries, force]);

  const handleClick = useCallback(() => {
    void handleBackfill();
  }, [handleBackfill]);

  return (
    <div className="container mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-8">Repository Analysis Backfill</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>Backfill Analysis Summaries</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              This will scan all configured repository analyses and generate missing summary files. 
              The operation is safe to re-run and will only process missing summaries.
            </p>
            <div className="flex items-center gap-2">
              <Checkbox checked={force} onCheckedChange={v => setForce(v === true)}/> Force
            </div>
            
            <Button 
              onClick={handleClick} 
              disabled={isBackfilling}
              className="flex items-center gap-2"
            >
              {isBackfilling && <Loader />} Backfill
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}