import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select.tsx";
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu.tsx";
import { Button } from "@/components/ui/button.tsx";
import { ChevronDown } from "lucide-react";
import { useRepositories } from "@/hooks/useRepositoryQueries.ts";
import { Loader } from "@/components/Loader.tsx";
import { ErrorAlert } from "@/components/ErrorAlert.tsx";

export interface RepositorySelectorProps {
  value?: string;
  onValueChange?: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
}

export function RepositorySelector({
  value,
  onValueChange,
  placeholder = "Select a repository...",
  disabled = false,
  className
}: RepositorySelectorProps) {
  const { repositories, loading, error } = useRepositories();

  if (loading) {
    return (
      <div className="flex items-center gap-2">
        <Loader />
        <span className="text-sm text-muted-foreground">Loading repositories...</span>
      </div>
    );
  }

  if (error) {
    return <ErrorAlert err={error} />;
  }

  if (!repositories || repositories.length === 0) {
    return (
      <div className="text-sm text-muted-foreground">
        No repositories available
      </div>
    );
  }

  return (
    <Select value={value} onValueChange={onValueChange} disabled={disabled}>
      <SelectTrigger className={className}>
        <SelectValue placeholder={placeholder} />
      </SelectTrigger>
      <SelectContent>
        {repositories.map((repo) => (
          <SelectItem key={repo.id} value={repo.id}>
            <div className="flex flex-col">
              <span className="font-medium">{repo.name}</span>
              {repo.fullName !== repo.name && (
                <span className="text-xs text-muted-foreground">{repo.fullName}</span>
              )}
            </div>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}

export interface MultiRepositorySelectorProps {
  value?: string[];
  onValueChange?: (value: string[]) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
}

export function MultiRepositorySelector({
  value = [],
  onValueChange,
  placeholder = "Select repositories...",
  disabled = false,
  className
}: MultiRepositorySelectorProps) {
  const { repositories, loading, error } = useRepositories();

  if (loading) {
    return (
      <div className="flex items-center gap-2">
        <Loader />
        <span className="text-sm text-muted-foreground">Loading repositories...</span>
      </div>
    );
  }

  if (error) {
    return <ErrorAlert err={error} />;
  }

  if (!repositories || repositories.length === 0) {
    return (
      <div className="text-sm text-muted-foreground">
        No repositories available
      </div>
    );
  }

  const selectedRepos = repositories.filter(repo => value.includes(repo.id));
  const displayText = selectedRepos.length > 0 
    ? `${selectedRepos.length} selected`
    : placeholder;

  const handleValueChange = (repoId: string) => {
    if (!onValueChange) return;
    
    const newValue = value.includes(repoId)
      ? value.filter(id => id !== repoId)
      : [...value, repoId];
    
    onValueChange(newValue);
  };

  return (
    <div className="space-y-2">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="outline"
            className={`w-full justify-between ${className}`}
            disabled={disabled}
          >
            <span className="truncate">{displayText}</span>
            <ChevronDown className="h-4 w-4 opacity-50" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="w-56" align="start">
          {repositories.map((repo) => (
            <DropdownMenuCheckboxItem
              key={repo.id}
              checked={value.includes(repo.id)}
              onCheckedChange={() => handleValueChange(repo.id)}
            >
              <div className="flex flex-col">
                <span className="font-medium">{repo.name}</span>
                {repo.fullName !== repo.name && (
                  <span className="text-xs text-muted-foreground">{repo.fullName}</span>
                )}
              </div>
            </DropdownMenuCheckboxItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>
      
      {selectedRepos.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {selectedRepos.map((repo) => (
            <span
              key={repo.id}
              className="inline-flex items-center gap-1 px-2 py-1 bg-secondary text-secondary-foreground rounded-md text-xs"
            >
              {repo.name}
              <button
                onClick={() => handleValueChange(repo.id)}
                className="ml-1 hover:bg-secondary-foreground/20 rounded-full p-0.5"
                disabled={disabled}
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}