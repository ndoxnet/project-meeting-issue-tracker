// Concept by MrHan (08974747477)
import type { IssueUpdateResponse } from '@/api/types';
import { formatDate, formatDateTime } from '@/lib/dates';
import { VoidUpdateButton } from './VoidUpdateButton';

/**
 * Chronological follow-up history (from GET /issues/:id/updates). When
 * `canVoid` is set (ADMIN) each non-voided entry offers a Void action.
 */
export function Timeline({
  updates,
  issueId,
  canVoid = false,
}: {
  updates: IssueUpdateResponse[];
  issueId?: string;
  canVoid?: boolean;
}) {
  return (
    <ol className="space-y-3">
      {updates.map((u) => (
        <li
          key={u.id}
          className={`rounded-lg border p-3 ${
            u.voided_at ? 'border-border bg-background opacity-70' : 'border-border bg-surface'
          }`}
        >
          <div className="flex flex-wrap items-center gap-2 text-xs text-muted">
            <span>{formatDate(u.update_date)}</span>
            {u.voided_at && (
              <span className="rounded-full border border-amber-200 bg-amber-50 px-2 py-0.5 font-medium text-amber-700">
                Voided
              </span>
            )}
            {canVoid && issueId && !u.voided_at && (
              <span className="ml-auto">
                <VoidUpdateButton issueId={issueId} update={u} />
              </span>
            )}
          </div>
          <p className="mt-1 text-sm text-text">{u.update_note}</p>
          {u.voided_at && u.void_reason && (
            <p className="mt-1 text-xs text-amber-700">Void reason: {u.void_reason}</p>
          )}
          {u.decision && <p className="mt-1 text-sm text-muted">Decision: {u.decision}</p>}
          {u.next_action && <p className="mt-1 text-sm text-muted">Next action: {u.next_action}</p>}
          <div className="mt-1 flex flex-wrap gap-x-3 gap-y-1 text-xs text-muted">
            {u.status_before && u.status_after && (
              <span>
                Status: {u.status_before} → {u.status_after}
              </span>
            )}
            {u.due_date_after && (
              <span>
                Due: {formatDate(u.due_date_before)} → {formatDate(u.due_date_after)}
              </span>
            )}
            {u.pic_after && (
              <span>
                PIC: {u.pic_before ?? '—'} → {u.pic_after}
              </span>
            )}
            {u.progress_percentage != null && <span>Progress: {u.progress_percentage}%</span>}
          </div>
          <div className="mt-1 text-xs text-muted">Recorded {formatDateTime(u.created_at)}</div>
        </li>
      ))}
    </ol>
  );
}
