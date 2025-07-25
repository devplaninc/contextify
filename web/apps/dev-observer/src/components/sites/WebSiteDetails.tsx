import React, {type ReactNode, useCallback, useMemo, useState} from "react";
import {useNavigate} from "react-router";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Button} from "@/components/ui/button.tsx";
import {useWebsite} from "@/hooks/useWebsiteQueries.ts";
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
import {ErrorAlert} from "@/components/ErrorAlert.tsx";
import {AnalysisList} from "@/components/analysis/AnalysisList.tsx";
import {normalizeDomain} from "@devplan/contextify-api";

interface WebSiteDetailsProps {
  websiteId: string;
}

const WebSiteDetails: React.FC<WebSiteDetailsProps> = ({websiteId}) => {
  const {website, error} = useWebsite(websiteId);
  const {rescanWebSite} = useBoundStore();
  const url = website?.url
  const domainName = useMemo(()=> {
    try {
      return url ? normalizeDomain(url) : undefined
    } catch {
      return undefined
    }
  }, [url])

  const rescan = useCallback(() => {
    rescanWebSite(websiteId)
      .then(() => toast.success(`Rescan started`))
      .catch(e => toast.error(`Failed to initialize rescan: ${e}`));
  }, [websiteId, rescanWebSite]);

  if (!website) {
    if (error) {
      return <ErrorAlert err={error}/>
    }
    return <Loader/>
  }


  return <div>
    <Card className="mb-8">
      <CardHeader>
        <CardTitle>Website Information</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <WebSiteProp name="URL" value={website.url}/>
          <WebSiteProp name="ID" value={website.id}/>
          <div className="flex gap-2 items-center">
            <DeleteWebSiteButton websiteId={websiteId}/>
            <Button onClick={rescan}>Rescan</Button>
          </div>
        </div>
      </CardContent>
    </Card>
    {domainName && <AnalysisList kind="websites" keysFiler={k => k.key.startsWith(domainName)} />}
  </div>
}

function WebSiteProp({name, value}: { name: ReactNode, value: ReactNode }) {
  return <div className="flex gap-2 items-center">
    <h3 className="text-sm font-medium text-muted-foreground">{name}:</h3>
    <p className="break-all">{value}</p>
  </div>
}

function DeleteWebSiteButton({websiteId}: { websiteId: string }) {
  const {deleteWebSite} = useBoundStore();
  const [deleting, setDeleting] = useState(false);
  const navigate = useNavigate();

  const onDelete = useCallback(() => {
    setDeleting(true);
    deleteWebSite(websiteId)
      .then(() => navigate("/websites"))
      .catch(e => {
        toast.error(`Failed to delete website: ${e}`);
        throw e;
      }).finally(() => setDeleting(false));
  }, [deleteWebSite, websiteId, navigate]);

  return <div>
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button variant="destructive">Delete</Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Are you sure you want to delete this website?</AlertDialogTitle>
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

export default WebSiteDetails;