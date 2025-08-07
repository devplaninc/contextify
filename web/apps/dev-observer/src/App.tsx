import {BrowserRouter, Navigate, Route, Routes} from 'react-router';
import {QueryClient, QueryClientProvider} from '@tanstack/react-query';
import RepositoryListPage from './pages/RepositoryListPage.tsx';
import RepositoryDetailsPage from './pages/RepositoryDetailsPage.tsx';
import WebSitesListPage from './pages/WebSitesListPage.tsx';
import WebSiteDetailsPage from './pages/WebSiteDetailsPage.tsx';
import GlobalConfigEditorPage from "@/pages/config/GlobalConfigEditorPage.tsx";
import {SidebarInset, SidebarProvider} from "@/components/ui/sidebar.tsx";
import {SiteHeader} from "@/components/layout/SiteHeader.tsx";
import {AppSidebar} from "@/components/layout/AppSidebar.tsx";
import {Toaster} from "@/components/ui/sonner.tsx"
import {useObservationKeys} from "@/hooks/useObservationQueries.ts";
import {useBoundStore} from "@/store/use-bound-store.tsx";
import {useEffect, useState} from "react";
import {Loader} from "@/components/Loader.tsx";
import {ErrorAlert} from "@/components/ErrorAlert.tsx";
import {ClerkProvider} from "@/auth/ClerkProvider.tsx";
import {ProcessingResultPage} from "@/pages/ProcessingResultPage.tsx";
import {processingResultPath} from "@/paths.tsx";
import ProcessingPage from "@/pages/ProcessingPage.tsx";
import TokensPage from "@/pages/TokensPage.tsx";

// Create a client
const queryClient = new QueryClient();

function App() {
  const [error, setError] = useState<Error | undefined>(undefined);
  const {fetchUsersConfig, usersStatus} = useBoundStore()
  useEffect(() => {
    if (usersStatus) {
      return
    }
    fetchUsersConfig().catch(setError)
  }, [fetchUsersConfig, usersStatus]);
  if (!usersStatus) {
    if (error) {
      return <ErrorAlert err={error}/>
    }
    return <Loader/>
  }

  return <div className="[--header-height:calc(theme(spacing.14))]">
    <Toaster/>
    <QueryClientProvider client={queryClient}>
      <ClerkProvider>
        <BrowserRouter>
          <SidebarProvider className="flex flex-col">
            <div className="min-h-screen bg-background text-foreground">
              <SiteHeader/>
              <div className="flex flex-1">
                <AppSidebar/>
                <SidebarInset>
                  <div className="p-4">
                    <AppRoutes/>
                  </div>
                </SidebarInset>
              </div>
            </div>
          </SidebarProvider>
        </BrowserRouter>
      </ClerkProvider>
    </QueryClientProvider>
  </div>;
}

function AppRoutes() {
  useObservationKeys("repos")
  useObservationKeys("websites")
  return <Routes>
    <Route path="/repositories" element={<RepositoryListPage/>}/>
    <Route path="/repositories/:id" element={<RepositoryDetailsPage/>}/>
    <Route path="/websites" element={<WebSitesListPage/>}/>
    <Route path="/websites/:id" element={<WebSiteDetailsPage/>}/>
    <Route path={processingResultPath(":id")} element={<ProcessingResultPage/>}/>
    <Route path="/processing" element={<ProcessingPage/>}/>
    <Route path="/repo_tokens" element={<TokensPage/>}/>

    <Route path="/admin/config-editor" element={<GlobalConfigEditorPage/>}/>
    <Route path="/" element={<Navigate to="/repositories" replace/>}/>
    <Route path="*" element={<Navigate to="/repositories" replace/>}/>
  </Routes>
}

export default App;
