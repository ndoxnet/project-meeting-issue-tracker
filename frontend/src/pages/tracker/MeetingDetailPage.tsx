// Concept by MrHan (08974747477)
import { Link, useParams } from 'react-router-dom';
import { ExternalLink, Pencil } from 'lucide-react';
import { usePageTitle } from '@/hooks/usePageTitle';
import { PageHeader } from '@/components/layout/PageHeader';
import { DataState } from '@/components/feedback/DataState';
import { IssueRow } from '@/components/tracker/IssueRow';
import { useAuth } from '@/auth/useAuth';
import { useOccurrence } from '@/api/meetings';
import { useMeetingTypes } from '@/api/masterdata';
import { useIssues } from '@/api/issues';
import { formatDate, formatDateTime } from '@/lib/dates';

export function MeetingDetailPage() {
  const { meetingId = '' } = useParams();
  const { hasRole } = useAuth();
  const occ = useOccurrence(meetingId);
  const types = useMeetingTypes();
  const issues = useIssues({ meeting_occurrence_id: meetingId, page: 1, page_size: 100 });
  usePageTitle('Meeting');

  const typeName = occ.data
    ? types.data?.items.find((t) => t.id === occ.data!.meeting_id)?.name
    : undefined;

  return (
    <section>
      <PageHeader
        title="Meeting"
        backTo="/app/meetings"
        backLabel="Back to meetings"
        actions={
          occ.data && hasRole('EDITOR', 'ADMIN') ? (
            <Link
              to={`/app/meetings/${meetingId}/edit`}
              className="inline-flex items-center gap-1 rounded-md border border-border bg-surface px-3 py-2 text-sm text-text hover:bg-background"
            >
              <Pencil className="h-4 w-4" aria-hidden="true" /> Edit
            </Link>
          ) : undefined
        }
      />
      <DataState isLoading={occ.isLoading} error={occ.error} loadingLabel="Loading meeting…">
        {occ.data && (
          <>
            <div className="rounded-lg border border-border bg-surface p-4">
              <h2 className="text-lg font-semibold text-text">{typeName ?? 'Meeting'}</h2>
              <dl className="mt-3 grid gap-2 sm:grid-cols-2">
                <Item label="Date" value={formatDate(occ.data.meeting_date)} />
                <Item label="Number" value={occ.data.meeting_number} />
                <Item label="Reference" value={occ.data.reference_number} />
                <Item label="Recorded" value={formatDateTime(occ.data.created_at)} />
              </dl>
              {occ.data.agenda && (
                <p className="mt-3 text-sm text-text">
                  <span className="font-medium">Agenda:</span> {occ.data.agenda}
                </p>
              )}
              {occ.data.notes && (
                <p className="mt-2 text-sm text-text">
                  <span className="font-medium">Notes:</span> {occ.data.notes}
                </p>
              )}
              {occ.data.minutes_link && (
                <a
                  href={occ.data.minutes_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-2 inline-flex items-center gap-1 text-sm text-primary hover:underline"
                >
                  <ExternalLink className="h-4 w-4" aria-hidden="true" /> Minutes
                </a>
              )}
            </div>

            <h2 className="mb-2 mt-6 text-sm font-semibold text-text">Issues raised in this meeting</h2>
            <DataState
              isLoading={issues.isLoading}
              error={issues.error}
              isEmpty={(issues.data?.items.length ?? 0) === 0}
              loadingLabel="Loading issues…"
              emptyTitle="No issues raised in this meeting"
            >
              <div className="space-y-2">
                {issues.data?.items.map((i) => <IssueRow key={i.id} issue={i} />)}
              </div>
            </DataState>
          </>
        )}
      </DataState>
    </section>
  );
}

function Item({ label, value }: { label: string; value: string | null }) {
  return (
    <div>
      <dt className="text-xs text-muted">{label}</dt>
      <dd className="text-sm text-text">{value ?? '—'}</dd>
    </div>
  );
}
