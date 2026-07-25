// Concept by MrHan (08974747477)
import { useState } from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider } from 'react-router-dom';
import { createQueryClient } from '@/api/queryClient';
import { AuthProvider } from '@/auth/AuthProvider';
import { ErrorBoundary } from '@/components/feedback/ErrorBoundary';
import { ToastProvider } from '@/components/feedback/ToastProvider';
import { router } from './router';

/**
 * Provider composition. Order: ErrorBoundary → QueryClientProvider → AuthProvider
 * (needs the query client to clear cache on logout/401) → RouterProvider (routes
 * consume auth via context).
 */
export function AppProviders() {
  const [queryClient] = useState(() => createQueryClient());
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <ToastProvider>
            <RouterProvider router={router} />
          </ToastProvider>
        </AuthProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
