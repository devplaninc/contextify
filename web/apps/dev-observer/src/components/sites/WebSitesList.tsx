import React, {useCallback, useState} from "react";
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { WebSite } from "@devplan/contextify-api";
import { useWebsites } from "@/hooks/useWebsiteQueries.ts";
import { Button } from "@/components/ui/button.tsx";
import { ErrorAlert } from "@/components/ErrorAlert.tsx";
import { Loader } from "@/components/Loader.tsx";
import { toast } from "sonner";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table.tsx";
import { ExternalLink, Trash2 } from "lucide-react";
import {useBoundStore} from "@/store/use-bound-store.tsx";
import { Link } from "react-router";

const columnHelper = createColumnHelper<WebSite>();

const WebSitesList: React.FC = () => {
  const { websites, error, loading } = useWebsites();
  const [deleting, setDeleting] = useState(false);
  const {deleteWebSite} = useBoundStore();

  const handleDelete = useCallback(async (id: string) => {
    setDeleting(true);
    await deleteWebSite(id)
      .catch(error => toast.error(`Failed to delete website: ${error}`))
      .then(() => toast.success("Website deleted successfully"))
      .finally(() => setDeleting(false));
  }, [deleteWebSite]);

  const columns = React.useMemo(
    () => [
      columnHelper.accessor("url", {
        header: "URL",
        cell: (info) => (
          <div className="flex items-center space-x-2">
            <Link 
              to={`/websites/${info.row.original.id}`}
              className="text-blue-500 hover:underline flex items-center"
            >
              {info.getValue()}
            </Link>
            <a 
              href={info.getValue()}
              target="_blank" 
              rel="noopener noreferrer"
              className="text-gray-500 hover:text-gray-700"
              title="Open in new tab"
            >
              <ExternalLink className="size-4" />
            </a>
          </div>
        ),
      }),
      columnHelper.accessor("id", {
        header: "Actions",
        cell: (info) => (
          <Button
            variant="ghost"
            size="icon"
            onClick={() => {
              void handleDelete(info.row.original.id)
            }}
            disabled={deleting}
          >
            <Trash2 className="size-4 text-red-500" />
          </Button>
        ),
      }),
    ],
    [deleting, handleDelete]
  );

  const table = useReactTable({
    data: websites ?? [],
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  if (loading) {
    return <Loader />;
  }

  if (error) {
    return <ErrorAlert err={error} />;
  }

  if (!websites || websites.length === 0) {
    return (
      <div className="bg-muted p-8 rounded-lg text-center">
        <h3 className="text-xl font-medium mb-2">No websites found</h3>
        <p className="text-muted-foreground mb-4">
          Add your first website using the form above.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows.map((row) => (
              <TableRow key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
};

export default WebSitesList;
