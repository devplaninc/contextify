import { useState, useEffect } from 'react';
import {usersStatusAPI} from '@/store/apiPaths.tsx';
import {GetUserManagementStatusResponse} from "@devplan/contextify-api";
import type { UserManagementStatus } from "@devplan/contextify-api";

export function useUserManagementStatus() {
  const [status, setStatus] = useState<UserManagementStatus | undefined>(undefined);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        setLoading(true);
        const status = await fetch(usersStatusAPI())
          .then(r => r.ok ? r.json() : Promise.reject(new Error(r.statusText)))
          .then(js => GetUserManagementStatusResponse.fromJSON(js).status);
        setStatus(status);
      } catch (err) {
        console.error('Error fetching user management status:', err);
        setError(err instanceof Error ? err : new Error(String(err)));
      } finally {
        setLoading(false);
      }
    };

    void fetchStatus()
  }, []);

  return { status, loading, error };
}