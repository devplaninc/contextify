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
import {GitHubChangesList} from "@/components/repos/GitHubChangesList.tsx";

const RepositoryDetailsPage: React.FC = () => {
  const {id} = useParams<{ id: string }>();
  const navigate = useNavigate();
  const {repository, loading, error} = useRepositoryQuery(id ?? '');
  const errorMessage = error instanceof Error ? error.message : 'An error occurred';
  const {rescanRepository} = useBoundStore()
  const rescan = useCallback(() => {
    rescanRepository(id!)
      .then(() => toast.success(`Rescan started`))
      .catch(e => toast.error(`Failed to initialize rescan: ${e}`))
  }, [id, rescanRepository])

  const handleBack = () => navigate("/repositories");

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
        <div>
          <h1 className="text-3xl font-bold mb-6">{repository.name}</h1>

          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Repository Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <RepoProp name="URL" value={repository.url}/>
                <RepoProp name="Full Name" value={repository.fullName}/>
                <RepoProp name="Description" value={repository.description}/>
                <RepoProp name="ID" value={repository.id}/>
                <RepoProp name="Installation id" value={repository.properties?.appInfo?.installationId}/>
                <RepoProp name="Size Kb" value={repository.properties?.meta?.sizeKb}/>
                <div className="flex gap-2 items-center">
                  <DeleteRepoButton repoId={id!}/>
                  <Button onClick={rescan}>Rescan</Button>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="space-y-6">
            <GitHubChangesList repo={repository}/>
            <RepoAnalysisList repo={repository}/>
          </div>
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

function RepoProp({name, value}: { name: ReactNode, value: ReactNode }) {
  return <div className="flex gap-2 items-center">
    <h3 className="text-sm font-medium text-muted-foreground">{name}:</h3>
    <p className="break-all">{value}</p>
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
