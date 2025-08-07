import React, { useState } from "react";
import { validateRepositoryUrl } from "@/utils/repositoryUtils.ts";
import type { ValidationError } from "@/types/repository.ts";
import { Input } from "@/components/ui/input.tsx";
import { Button } from "@/components/ui/button.tsx";
import { Label } from "@/components/ui/label.tsx";
import { Alert, AlertDescription } from "@/components/ui/alert.tsx";
import { useAddRepositoryMutation } from "@/hooks/useRepositoryQueries.ts";
import {useBoundStore} from "@/store/use-bound-store.tsx";

const AddRepositoryForm: React.FC = () => {
  const [url, setUrl] = useState("");
  const [validationError, setValidationError] = useState<ValidationError | null>(
    null
  );
  const {repositories} = useBoundStore()

  const validateInput = (value: string): boolean => {
    const error = validateRepositoryUrl(value, repositories);
    setValidationError(error);
    return !error;
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setUrl(value);
    if (value) {
      validateInput(value);
    } else {
      setValidationError(null);
    }
  };

  const { mutate: addRepository, isPending: loading, error: mutationError } = useAddRepositoryMutation();
  const errorMessage = mutationError instanceof Error ? mutationError.message : 'Failed to add repository';

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateInput(url)) {
      return;
    }

    addRepository(url, {
      onSuccess: () => {
        setUrl("");
        setValidationError(null);
      },
      onError: (err: unknown) => {
        const error = err as Error & { errors?: ValidationError[] };
        if (error.errors && error.errors.length > 0) {
          setValidationError(error.errors[0]);
        }
        console.error("Error adding repository:", error);
      }
    });
  };

  return (
    <div className="bg-card border rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">Add Repository</h2>
      <form onSubmit={handleSubmit}>
        <div className="space-y-4">
          <div>
            <Label htmlFor="repository-url">Repository URL</Label>
            <Input
              id="repository-url"
              placeholder="https://github.com/owner/repo, https://bitbucket.org/owner/repo, or SSH format"
              value={url}
              onChange={handleInputChange}
              className={validationError ? "border-destructive" : ""}
              disabled={loading}
            />
            {validationError && (
              <p className="text-destructive text-sm mt-1">
                {validationError.message}
              </p>
            )}
          </div>

          {mutationError ? (
            <Alert variant="destructive">
              <AlertDescription>
                {errorMessage}
              </AlertDescription>
            </Alert>
          ) : null}

          <Button type="submit" disabled={loading || !url}>
            {loading ? "Adding..." : "Add Repository"}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default AddRepositoryForm;
