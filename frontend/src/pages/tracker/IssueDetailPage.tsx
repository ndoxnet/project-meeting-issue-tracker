// Concept by MrHan (08974747477)
import type { ReactNode } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Pencil } from 'lucide-react';
import { usePageTitle } from '@/hooks/usePageTitle';
import { PageHeader } from '@/components/layout/PageHeader';
import { DataState } from '@/components/feedback/DataState';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { PriorityBadge } from '@/components/ui/PriorityBadge';
import { Timeline } from '@/features/issues/Timeline';
import { IssueActions } from '@/features/issues/IssueActions';
import { AttachmentsPanel } from '@/features/attachments/AttachmentsPanel';
import { canEditMetadata } from '@/features/issues/lifecycle';
import { useAuth } from '@/auth/useAuth';
import { useIssue, useIssueUpdates } from '@/api/issues';
import { formatDate, formatDateTime } from '@/lib/dates';

function Row({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="flex flex-col border-b border-border py-2 sm:flex-row sm:items-center">
      <dt className="w-48 shrink-0 text-sm text-muted">{label}</dt>
      <dd className="text-sm text-text">{value ?? '—'}</dd>
    </div>
  );
}

export function IssueDetailPage() {
  const { issueId = '' } = useParams();
  const { hasRole } = useAuth();
  const issue = useIssue(issueId);
  const updates = useIssueUpdates(issueId);
  usePageTitle(issue.data ? issue.data.issue_code : 'Issue');

  const canEdit = hasRole('EDITOR', 'ADMIN');

  return (
    <section>
      <PageHeader title="Issue" backTo="/app/issues" backLabel="Back to issues" />
      <DataState
        isLoading={issue.isLoading}
        error={issue.error}
        loadingLabel="Loading issue…"
      >
        {issue.data && (
          <>
            <div className="rounded-lg border border-border bg-surface p-4">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-xs text-muted">{issue.data.issue_code}</span>
                <StatusBadge status={issue.data.status} />
                <PriorityBadge priority={issue.data.priority} />
                {issue.data.archived_at && (
                  <span className="rounded-full border border-border bg-background px-2 py-0.5 text-xs text-muted">
                    Archived
                  </span>
                )}
              </div>
              <h2 className="mt-2 text-lg font-semibold text-text">{issue.data.title}</h2>

              {canEdit && (
                <div className="mt-3 flex flex-wrap items-center gap-2">
                  {canEditMetadata(issue.data.status, issue.data.archived_at != null) && (
                    <Link
                      to={`/app/issues/${issue.data.id}/edit`}
                      className="inline-flex items-center gap-1 rounded-md border border-border bg-surface px-3 py-2 text-sm text-text hover:bg-background"
                    >
                      <Pencil className="h-4 w-4" aria-hidden="true" /> Edit
                    </Link>
                  )}
                  {!issue.data.archived_at && <IssueActions issue={issue.data} />}
                </div>
              )}

              <dl className="mt-4">
                <Row label="Description" value={issue.data.description} />
                <Row label="Category" value={issue.data.category_name} />
                <Row label="Responsible party" value={issue.data.responsible_party_name} />
                <Row label="PIC" value={issue.data.pic_name} />
                <Row label="Raised date" value={formatDate(issue.data.raised_date)} />
                <Row label="Due date" value={formatDate(issue.data.due_date)} />
                <Row label="Days open" value={issue.data.days_open} />
                <Row label="Next action" value={issue.data.next_action} />
                <Row
                  label="Last update"
                  value={
                    issue.data.last_update_at
                      ? formatDateTime(issue.data.last_update_at)
                      : `No follow-up yet (${issue.data.days_since_last_update}d since raised)`
                  }
                />
                {issue.data.closed_date && (
                  <>
                    <Row label="Closed date" value={formatDate(issue.data.closed_date)} />
                    <Row label="Closure note" value={issue.data.closure_note} />
                  </>
                )}
                {issue.data.reopened_at && (
                  <Row label="Reopened at" value={formatDateTime(issue.data.reopened_at)} />
                )}
              </dl>
            </div>

            <h2 className="mb-2 mt-6 text-sm font-semibold text-text">Follow-up timeline</h2>
            <DataState
              isLoading={updates.isLoading}
              error={updates.error}
              isEmpty={(updates.data?.length ?? 0) === 0}
              loadingLabel="Loading timeline…"
              emptyTitle="No follow-up updates yet"
            >
              {updates.data && <Timeline updates={updates.data} />}
            </DataState>

            <AttachmentsPanel issueId={issue.data.id} archived={issue.data.archived_at != null} />
          </>
        )}
      </DataState>
    </section>
  );
}
