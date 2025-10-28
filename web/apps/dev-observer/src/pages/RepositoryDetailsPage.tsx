import React, {type ReactNode, useCallback, useState} from "react";
import {useNavigate, useParams} from "react-router";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Button} from "@/components/ui/button.tsx";
import {Alert, AlertDescription, AlertTitle} from "@/components/ui/alert.tsx";
import {useRepositoryQuery} from "@/hooks/useRepositoryQueries.ts";
import {useBoundStore} from "@/store/use-bound-store.tsx";
import {toast} from "sonner";
import {Loader} from "@/components/Loader.tsx";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger
} from "@/components/ui/alert-dialog.tsx";
import {RepoAnalysisList} from "@/components/repos/RepoAnalysisList.tsx";
import {ProcessingResults} from "@/components/processing/ProcessingResults.tsx";
import {RequestRepoChangesSummaryButton} from "@/components/processing/RequestRepoChangesSummaryButton.tsx";
import {Tabs, TabsContent, TabsList, TabsTrigger} from "@/components/ui/tabs.tsx";

const RepositoryDetailsPage: React.FC = () => {
  const {id} = useParams<{ id: string }>();
  const navigate = useNavigate();
  const {repository, loading, error} = useRepositoryQuery(id ?? '');
  const errorMessage = error instanceof Error ? error.message : 'An error occurred';
  const {rescanRepository, analyzeTokens} = useBoundStore()
  const rescan = useCallback(() => {
    rescanRepository(id!)
      .then(() => toast.success(`Rescan started`))
      .catch(e => toast.error(`Failed to initialize rescan: ${e}`))
  }, [id, rescanRepository])
  const research = useCallback(() => {
    rescanRepository(id!, {research: true, skipSummary: true})
      .then(() => toast.success(`Research started`))
      .catch(e => toast.error(`Failed to initialize research: ${e}`))
  }, [id, rescanRepository])

  const forcedResearch = useCallback(() => {
    rescanRepository(id!, {research: true, skipSummary: true, forceResearch: true})
      .then(() => toast.success(`Research started`))
      .catch(e => toast.error(`Failed to initialize research: ${e}`))
  }, [id, rescanRepository])
  const runTokenAnalysis = useCallback(() => {
    analyzeTokens(id!)
      .then(() => toast.success(`Tokens processed`))
      .catch(e => toast.error(`Failed to analyze tokens: ${e}`))
  }, [analyzeTokens, id])

  const handleBack = () => navigate("/repositories");
  const tokensInfo = repository?.properties?.meta?.tokensInfo

  return (
    <div className="container mx-auto py-8 px-4">
      {error ? (
        <Alert variant="destructive" className="mb-6">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{errorMessage}</AlertDescription>
        </Alert>
      ) : null}

      {loading ? (
        <div className="flex justify-center items-center py-12">
          <p className="text-lg">Loading repository details...</p>
        </div>
      ) : repository ? (
        <div className="space-y-8">
          <h1 className="text-3xl font-bold">{repository.name}</h1>

          <Card>
            <CardHeader>
              <CardTitle>Repository Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <RepoProp name="URL">{repository.url}</RepoProp>
                <RepoProp name="Full Name">{repository.fullName}</RepoProp>
                <RepoProp name="Description">{repository.description}</RepoProp>
                <RepoProp name="ID">{repository.id}</RepoProp>
                <RepoProp name="Installation id">{repository.properties?.appInfo?.installationId}</RepoProp>
                <RepoProp name="Size Kb">{repository.properties?.meta?.sizeKb}</RepoProp>
                <RepoProp name="Tokens Count">{tokensInfo?.tokensCount}</RepoProp>
                <RepoProp name="Tokens Updated At">{tokensInfo?.createdAt?.toLocaleString()}</RepoProp>
                <div className="flex gap-2 items-center">
                  <DeleteRepoButton repoId={id!}/>
                </div>
              </div>
            </CardContent>
          </Card>
          <Tabs defaultValue="analysis" className="space-y-4">
            <TabsList>
              <TabsTrigger value="analysis">Repo Analysis</TabsTrigger>
              <TabsTrigger value="changes">Change Reports</TabsTrigger>
            </TabsList>
            <TabsContent value="analysis">
              <div className="space-y-4">
                <div className="flex gap-2 items-center">
                  <Button onClick={rescan}>Rescan</Button>
                  <Button onClick={research}>Research</Button>
                  <Button onClick={forcedResearch}>Forced Research</Button>
                  <Button onClick={runTokenAnalysis}>Analyze tokens</Button>
                </div>
                <RepoAnalysisList repo={repository}/>
              </div>
            </TabsContent>
            <TabsContent value="changes">
              <div className="space-y-4">
                <RequestRepoChangesSummaryButton gitRepoId={repository.id}/>
                <ProcessingResults referenceId={repository.id}/>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      ) : (
        <div className="bg-muted p-8 rounded-lg text-center">
          <h3 className="text-xl font-medium mb-2">Repository not found</h3>
          <p className="text-muted-foreground mb-4">
            The repository you're looking for doesn't exist or has been removed.
          </p>
          <Button onClick={() => {
            void handleBack();
          }}>Go Back to Repository List</Button>
        </div>
      )}
    </div>
  );
};

function RepoProp({name, children}: { name: ReactNode, children: ReactNode }) {
  if (!children) {
    return null;
  }
  return <div className="flex gap-2 items-center">
    <h3 className="text-sm font-medium text-muted-foreground">{name}:</h3>
    <div>{children}</div>
  </div>
}

function DeleteRepoButton({repoId}: { repoId: string }) {
  const {deleteRepository} = useBoundStore()
  const [deleting, setDeleting] = useState(false);
  const navigate = useNavigate();
  const onDelete = useCallback(() => {
    setDeleting(true);
    deleteRepository(repoId)
      .then(() => navigate("/repositories"))
      .catch(e => {
        toast.error(`Failed to delete repo: ${e}`)
        throw e
      }).finally(() => setDeleting(false));
  }, [deleteRepository, repoId, navigate])
  return <div>
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button variant="destructive">Delete</Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Are you sure you want to delete repo?</AlertDialogTitle>
          <AlertDialogDescription>
            This action cannot be undone.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction asChild>
            <Button onClick={onDelete} disabled={deleting}>{deleting && <Loader/>} Delete</Button>
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  </div>
}

export default RepositoryDetailsPage;
