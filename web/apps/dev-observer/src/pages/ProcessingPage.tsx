import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card.tsx";
import { RequestRepoChangesSummaryButton } from "@/components/processing/RequestRepoChangesSummaryButton.tsx";
import { RequestAggregatedSummaryButton } from "@/components/processing/RequestAggregatedSummaryButton.tsx";

const ProcessingPage: React.FC = () => {
  return (
    <div className="container mx-auto py-8 px-4">
      <div className="space-y-8">
        <h1 className="text-3xl font-bold">Processing Requests</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Single Repository Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Generate a git changes report for a single repository. Select a repository 
                and configure the analysis parameters.
              </p>
              <RequestRepoChangesSummaryButton />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Multi-Repository Aggregated Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Generate an aggregated summary across multiple repositories. Select 
                multiple repositories and configure the aggregation parameters.
              </p>
              <RequestAggregatedSummaryButton />
            </CardContent>
          </Card>
        </div>

        <div className="mt-8">
          <Card>
            <CardHeader>
              <CardTitle>How to Use</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 text-sm">
                <div>
                  <h4 className="font-medium">Single Repository Analysis</h4>
                  <p className="text-muted-foreground">
                    Use this to analyze changes in a specific repository over a defined period. 
                    Perfect for understanding recent development activity in a single project.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium">Multi-Repository Aggregated Summary</h4>
                  <p className="text-muted-foreground">
                    Use this to get a comprehensive overview across multiple repositories. 
                    Ideal for understanding organization-wide development trends and activity patterns.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default ProcessingPage;