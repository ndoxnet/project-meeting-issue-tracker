// Concept by MrHan (08974747477)
import { QueryClient } from '@tanstack/react-query';
import { ApiError } from './errors';

// Do not retry these — they are deterministic client/auth errors.
const NO_RETRY_STATUS = new Set([400, 401, 403, 404, 409, 413, 415, 422]);

export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // At most one retry for transient network/5xx errors.
        retry: (failureCount, error) => {
          if (error instanceof ApiError && NO_RETRY_STATUS.has(error.status)) return false;
          return failureCount < 1;
        },
        staleTime: 30_000,
        refetchOnWindowFocus: false,
      },
      mutations: {
        retry: false, // never auto-retry mutations
      },
    },
  });
}
