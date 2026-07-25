// Concept by MrHan (08974747477)
import type { ReactNode } from 'react';
import { PageLoading } from './LoadingScreen';
import { InlineError } from './InlineError';
import { EmptyState } from './EmptyState';

/**
 * Renders the appropriate state for a data query: loading, error, empty, or the
 * children (success). Keeps pages consistent and DRY.
 */
export function DataState({
  isLoading,
  error,
  isEmpty,
  loadingLabel = 'Loading…',
  emptyTitle = 'Nothing to show',
  emptyDescription,
  emptyAction,
  children,
}: {
  isLoading: boolean;
  error: unknown;
  isEmpty?: boolean;
  loadingLabel?: string;
  emptyTitle?: string;
  emptyDescription?: string;
  emptyAction?: ReactNode;
  children: ReactNode;
}) {
  if (isLoading) return <PageLoading label={loadingLabel} />;
  if (error) return <InlineError error={error} />;
  if (isEmpty)
    return <EmptyState title={emptyTitle} description={emptyDescription} action={emptyAction} />;
  return <>{children}</>;
}
