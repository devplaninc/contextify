import React from "react";
import TokenForm from "./TokenForm.tsx";
import TokenTable from "./TokenTable.tsx";
import {useTokens} from "@/hooks/useTokenQueries.ts";
import {ErrorAlert} from "@/components/ErrorAlert.tsx";
import {Loader} from "@/components/Loader.tsx";

const TokenManagement: React.FC = () => {
  const {tokens, error, reload} = useTokens();

  const handleTokenAdded = () => {
    void reload();
  };

  const handleRefresh = () => {
    void reload();
  };
  if (tokens === undefined) {
    if (error) {
      return <ErrorAlert err={error}/>;
    }
    return <Loader/>
  }

  return (
    <div className="space-y-6">
      <TokenForm onSuccess={handleTokenAdded}/>
      <TokenTable tokens={tokens} onRefresh={handleRefresh}/>
    </div>
  );
};

export default TokenManagement;