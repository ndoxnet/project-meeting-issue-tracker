// Concept by MrHan (08974747477)
import { AlertTriangle } from 'lucide-react';
import { ApiError } from '@/api/errors';

/**
 * Inline error with an optional, expandable technical detail (request id).
 * Backend messages are rendered as plain text (never as HTML).
 */
export function InlineError({ error, className }: { error: unknown; className?: string }) {
  const message = toMessage(error);
  const requestId = error instanceof ApiError ? error.requestId : undefined;

  return (
    <div
      role="alert"
      className={`rounded-md border border-danger/30 bg-danger/5 p-3 text-sm text-danger ${className ?? ''}`}
    >
      <div className="flex items-start gap-2">
        <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
        <span>{message}</span>
      </div>
      {requestId && (
        <details className="mt-2 text-xs text-muted">
          <summary className="cursor-pointer">Technical details</summary>
          <div className="mt-1">
            Request ID: <code className="font-mono">{requestId}</code>
          </div>
        </details>
      )}
    </div>
  );
}

function toMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  if (error instanceof Error) return error.message;
  return 'Something went wrong.';
}
