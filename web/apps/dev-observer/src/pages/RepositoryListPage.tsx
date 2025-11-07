import React, {useMemo, useState} from "react";
import { Link } from "react-router";
import { Button } from "@/components/ui/button.tsx";
import { Input } from "@/components/ui/input.tsx";
import AddRepositoryForm from "@/components/AddRepositoryForm.tsx";
import { useRepositories } from "@/hooks/useRepositoryQueries.ts";
import { ErrorAlert } from "@/components/ErrorAlert.tsx";
import { Loader } from "@/components/Loader.tsx";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table.tsx";
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  useReactTable,
  type SortingState,
} from "@tanstack/react-table";
import type { GitRepository } from "@devplan/contextify-api";
import { toast } from "sonner";
import { useBoundStore } from "@/store/use-bound-store.tsx";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu.tsx";
import {cn} from "@/lib/utils.ts";
import {Ellipsis} from "lucide-react";

const c = createColumnHelper<GitRepository>();

const RepositoryListPage: React.FC = () => {
  const { repositories, error, reload } = useRepositories();
  const { analyzeTokens } = useBoundStore();

  const columns = useMemo(
    () => [
      c.accessor((row) => row.fullName?.split("/")?.[0] ?? "", {
        id: "owner",
        header: "Owner",
        enableSorting: true,
        enableGlobalFilter: true,
        cell: (info) => <span>{info.getValue() || "-"}</span>,
      }),
      c.accessor("name", {
        header: "Name",
        enableSorting: true,
        enableGlobalFilter: true,
        cell: (info) => (
          <Link
            to={`/repositories/${info.row.original.id}`}
            className="text-blue-500 hover:underline"
          >
            {info.getValue()}
          </Link>
        ),
      }),
      c.accessor("url", {
        header: "URL",
        enableSorting: true,
        enableGlobalFilter: true,
        cell: (info) => (
          <p className="text-sm text-muted-foreground break-all">
            {info.getValue()}
          </p>
        ),
      }),
      c.accessor(
        (row) => row.properties?.meta?.tokensInfo?.tokensCount,
        {
          id: "tokensCount",
          header: "Tokens",
          enableSorting: true,
          enableGlobalFilter: false,
          sortingFn: (a, b, columnId) => {
            const va = (a.getValue<number | undefined>(columnId) ?? Number.NEGATIVE_INFINITY);
            const vb = (b.getValue<number | undefined>(columnId) ?? Number.NEGATIVE_INFINITY);
            return va === vb ? 0 : va > vb ? 1 : -1;
          },
          cell: (info) => {
            const value = info.getValue();
            return <span>{value ?? "-"}</span>;
          },
        },
      ),
      c.display({
        id: "actions",
        header: "Actions",
        enableSorting: false,
        cell: (info) => {
          const repo = info.row.original;
          return (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="cursor-pointer"><Ellipsis className="size-4"/></Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem asChild>
                  <Link to={`/repositories/${repo.id}`}>View details</Link>
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => {
                    void analyzeTokens(repo.id)
                      .then(() => toast.success("Tokens recalculation started"))
                      .catch((e) => toast.error(`Failed to analyze tokens: ${e}`))
                      .finally(() => void reload());
                  }}
                >
                  Recalculate tokens
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          );
        },
      }),
    ],
    [analyzeTokens, reload],
  );

  const [sorting, setSorting] = useState<SortingState>([
    { id: "owner", desc: false },
    { id: "name", desc: false },
  ]);
  const [globalFilter, setGlobalFilter] = useState("");

  const table = useReactTable({
    data: repositories ?? [],
    columns,
    state: { sorting, globalFilter },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });

  // Total tokens for the current filtered rows (filtered data only)
  const filteredRows = table.getFilteredRowModel().rows;
  const totalTokens = useMemo(() =>
    filteredRows.reduce((sum, row) => {
      const v = row.getValue<number | undefined>("tokensCount");
      return sum + (typeof v === "number" && Number.isFinite(v) ? v : 0);
    }, 0),
  [filteredRows]);

  if (repositories === undefined) {
    if (error) {
      return <ErrorAlert err={error} />;
    }
    return <Loader />;
  }

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Repositories</h1>

      <div>
        <AddRepositoryForm />
      </div>

      <div className="flex justify-end">
        <div className="w-full md:max-w-xs">
          <Input
            value={globalFilter ?? ""}
            onChange={(e) => setGlobalFilter(e.target.value)}
            placeholder="Filter by owner, name, or URL"
          />
        </div>
      </div>

      {repositories.length === 0 ? (
        <div className="bg-muted p-8 rounded-lg text-center">
          <h3 className="text-xl font-medium mb-2">No repositories found</h3>
          <p className="text-muted-foreground mb-4">
            Add your first repository using the form above.
          </p>
        </div>
      ) : (
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              {table.getHeaderGroups().map((headerGroup) => (
                <TableRow key={headerGroup.id}>
                  {headerGroup.headers.map((header) => (
                    <TableHead key={header.id}>
                      {header.isPlaceholder ? null : (
                        <Button
                          variant="ghost"
                          size="sm"
                          className={cn("w-full", header.column.getCanSort() ? 'cursor-pointer' : 'cursor-default')}
                          onClick={header.column.getToggleSortingHandler()}
                          disabled={!header.column.getCanSort()}
                        >
                          {flexRender(header.column.columnDef.header, header.getContext())}
                          {header.column.getCanSort() ? (
                            <span className="text-xs text-muted-foreground">
                              {header.column.getIsSorted() === 'asc' ? '↑' : header.column.getIsSorted() === 'desc' ? '↓' : ''}
                            </span>
                          ) : null}
                        </Button>
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
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext(),
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
              <TableRow className="bg-muted/30 font-medium">
                {table.getVisibleLeafColumns().map((column) => (
                  <TableCell key={column.id}>
                    {column.id === "owner"
                      ? "Total"
                      : column.id === "tokensCount"
                        ? totalTokens.toLocaleString()
                        : ""}
                  </TableCell>
                ))}
              </TableRow>
            </TableBody>
          </Table>
        </div>
      )}

      {repositories.length > 0 && (
        <div className="mt-6 text-center">
          <Button
            onClick={() => {
              void reload();
            }}
            variant="outline"
          >
            Refresh Repositories
          </Button>
        </div>
      )}
    </div>
  );
};

export default RepositoryListPage;
