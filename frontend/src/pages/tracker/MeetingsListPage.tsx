// Concept by MrHan (08974747477)
import { Link, useSearchParams } from 'react-router-dom';
import { Plus } from 'lucide-react';
import { usePageTitle } from '@/hooks/usePageTitle';
import { PageHeader } from '@/components/layout/PageHeader';
import { DataState } from '@/components/feedback/DataState';
import { Pagination } from '@/components/ui/Pagination';
import { MeetingCard } from '@/components/tracker/MeetingCard';
import { Select } from '@/components/ui/Field';
import { useAuth } from '@/auth/useAuth';
import { useOccurrences } from '@/api/meetings';
import { useMeetingTypes } from '@/api/masterdata';

export function MeetingsListPage() {
  usePageTitle('Meetings');
  const { hasRole } = useAuth();
  const [params, setParams] = useSearchParams();
  const types = useMeetingTypes();

  const page = Number(params.get('page') ?? '1');
  const meetingId = params.get('meeting_id') ?? undefined;
  const occurrences = useOccurrences({ page, page_size: 20, meeting_id: meetingId });

  const typeName = new Map((types.data?.items ?? []).map((t) => [t.id, t.name]));

  function setType(value: string) {
    const next = new URLSearchParams(params);
    if (value) next.set('meeting_id', value);
    else next.delete('meeting_id');
    next.delete('page');
    setParams(next);
  }
  function setPage(next: number) {
    const p = new URLSearchParams(params);
    p.set('page', String(next));
    setParams(p);
  }

  return (
    <section>
      <PageHeader
        title="Meetings"
        description="Recorded meeting occurrences and their issues."
        actions={
          hasRole('EDITOR', 'ADMIN') ? (
            <Link
              to="/app/meetings/new"
              className="inline-flex items-center gap-1 rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-fg"
            >
              <Plus className="h-4 w-4" aria-hidden="true" /> New occurrence
            </Link>
          ) : undefined
        }
      />
      <div className="mb-4 max-w-xs">
        <Select
          value={meetingId ?? ''}
          onChange={(e) => setType(e.target.value)}
          className="mt-0"
          aria-label="Filter by meeting type"
        >
          <option value="">All meeting types</option>
          {types.data?.items.map((t) => (
            <option key={t.id} value={t.id}>
              {t.name}
            </option>
          ))}
        </Select>
      </div>

      <DataState
        isLoading={occurrences.isLoading}
        error={occurrences.error}
        isEmpty={(occurrences.data?.items.length ?? 0) === 0}
        loadingLabel="Loading meetings…"
        emptyTitle="No meetings recorded"
        emptyDescription="Meeting occurrences will appear here once recorded."
      >
        <div className="grid gap-3 sm:grid-cols-2">
          {occurrences.data?.items.map((occ) => (
            <MeetingCard key={occ.id} occurrence={occ} typeName={typeName.get(occ.meeting_id)} />
          ))}
        </div>
        {occurrences.data && <Pagination meta={occurrences.data.meta} onPageChange={setPage} />}
      </DataState>
    </section>
  );
}
