import React from "react";
import TokenManagement from "@/components/tokens/TokenManagement.tsx";

const TokensPage: React.FC = () => {
  return (
    <div className="container mx-auto py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Token Management</h1>
        <p className="text-muted-foreground">
          Manage your repository access tokens for GitHub and BitBucket.
        </p>
      </div>
      
      <TokenManagement />
    </div>
  );
};

export default TokensPage;