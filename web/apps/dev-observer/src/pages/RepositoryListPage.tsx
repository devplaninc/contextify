import React from "react";
import {Link} from "react-router";
import {Card, CardContent, CardFooter, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Button} from "@/components/ui/button.tsx";
import AddRepositoryForm from "@/components/AddRepositoryForm.tsx";
import {useRepositories} from "@/hooks/useRepositoryQueries.ts";
import {ErrorAlert} from "@/components/ErrorAlert.tsx";
import {Loader} from "@/components/Loader.tsx";

const RepositoryListPage: React.FC = () => {
  const {repositories, error, reload} = useRepositories();

  if (repositories === undefined) {
    if (error) {
      return <ErrorAlert err={error}/>
    }
    return <Loader/>
  }

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Repositories</h1>

      <div>
        <AddRepositoryForm/>
      </div>

      {repositories.length === 0 ? (
        <div className="bg-muted p-8 rounded-lg text-center">
          <h3 className="text-xl font-medium mb-2">No repositories found</h3>
          <p className="text-muted-foreground mb-4">
            Add your first repository using the form above.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {repositories.map(repo => (
            <Link to={`/repositories/${repo.id}`} key={repo.id}>
              <Card className="h-full hover:shadow-md transition-shadow cursor-pointer">
                <CardHeader>
                  <CardTitle>{repo.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground break-all">{repo.url}</p>
                </CardContent>
                <CardFooter>
                  <Button variant="outline" size="sm">View Details</Button>
                </CardFooter>
              </Card>
            </Link>
          ))}
        </div>
      )}

      {repositories.length > 0 && (
        <div className="mt-6 text-center">
          <Button onClick={() => {
            void reload();
          }} variant="outline">
            Refresh Repositories
          </Button>
        </div>
      )}
    </div>
  );
};

export default RepositoryListPage;
