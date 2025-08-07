import React, {useState} from "react";
import {format} from "date-fns";
import {GitProvider, type RepoToken} from "@devplan/contextify-api";

import {Button} from "@/components/ui/button.tsx";
import {Badge} from "@/components/ui/badge.tsx";
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow,} from "@/components/ui/table.tsx";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {useBoundStore} from "@/store/use-bound-store.tsx";

interface TokenTableProps {
  tokens: RepoToken[];
  onRefresh?: () => void;
}

const TokenTable: React.FC<TokenTableProps> = ({ tokens, onRefresh }) => {
  const {deleteToken} = useBoundStore();
  const [deleting, setDeleting] = useState(false);

  const handleDelete = (tokenId: string) => {
    setDeleting(true);
    void deleteToken(tokenId).then(() => {onRefresh?.()}).finally(() => setDeleting(false));
  };

  const getProviderName = (provider: GitProvider) => {
    switch (provider) {
      case GitProvider.GITHUB:
        return "GitHub";
      case GitProvider.BIT_BUCKET:
        return "BitBucket";
      default:
        return "Unknown";
    }
  };

  const formatDate = (date: Date | undefined) => {
    if (!date) return "N/A";
      return format(date, "MMM dd, yyyy HH:mm");
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Existing Tokens</CardTitle>
        <Button onClick={onRefresh} variant="outline" size="sm">
          Refresh
        </Button>
      </CardHeader>
      <CardContent>
        {tokens.length === 0 ? (
          <p className="text-muted-foreground text-center py-4">No tokens found</p>
        ) : (
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Namespace</TableHead>
                  <TableHead>Provider</TableHead>
                  <TableHead>Workspace</TableHead>
                  <TableHead>Repository</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Expires</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {tokens.map((token) => (
                  <TableRow key={token.id}>
                    <TableCell className="font-medium">{token.namespace}</TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {getProviderName(token.provider)}
                      </Badge>
                    </TableCell>
                    <TableCell>{(token.workspace) ?? "—"}</TableCell>
                    <TableCell>{(token.repo) ?? "—"}</TableCell>
                    <TableCell>
                      {(token.system) ? (
                        <Badge variant="secondary">System</Badge>
                      ) : (
                        <Badge variant="default">Manual</Badge>
                      )}
                    </TableCell>
                    <TableCell>
                        <span className="text-sm">
                          {formatDate(token.expiresAt)}
                        </span>
                    </TableCell>
                    <TableCell>
                      <span className="text-sm">
                        {formatDate(token.createdAt as { seconds: number; nanos: number })}
                      </span>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => handleDelete(token.id)}
                        disabled={deleting}
                      >
                        Delete
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default TokenTable;