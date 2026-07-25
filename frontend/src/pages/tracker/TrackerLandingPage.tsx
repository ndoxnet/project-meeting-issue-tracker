// Concept by MrHan (08974747477)
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ListChecks, CalendarDays } from 'lucide-react';
import { usePageTitle } from '@/hooks/usePageTitle';
import { PageHeader } from '@/components/layout/PageHeader';
import { StatCard } from '@/components/ui/StatCard';
import { DataState } from '@/components/feedback/DataState';
import { InlineError } from '@/components/feedback/InlineError';
import { IssueRow } from '@/components/tracker/IssueRow';
import { MeetingCard } from '@/components/tracker/MeetingCard';
import { DistributionBars } from '@/features/dashboard/DistributionBars';
import { TrendTable } from '@/features/dashboard/TrendTable';
import {
  useByCategory,
  useByResponsibleParty,
  useDashboardSummary,
  useOpenedVsClosed,
  useRecentlyUpdated,
} from '@/api/dashboard';
import { useOccurrences } from '@/api/meetings';
import { useMeetingTypes } from '@/api/masterdata';

const TREND_MONTHS = [6, 12, 24] as const;

export function TrackerLandingPage() {
  usePageTitle('Dashboard');
  const summary = useDashboardSummary();
  const recent = useRecentlyUpdated(5);
  const meetings = useOccurrences({ page: 1, page_size: 5 });
  const types = useMeetingTypes();

  const [months, setMonths] = useState<number>(6);
  const byCategory = useByCategory();
  const byResponsibleParty = useByResponsibleParty();
  const trend = useOpenedVsClosed(months);

  const typeName = new Map((types.data?.items ?? []).map((t) => [t.id, t.name]));

  return (
    <section>
      <PageHeader
        title="Project Control Dashboard"
        description="Overview of meetings and issues."
        actions={
          <div className="flex gap-2">
            <Link
              to="/app/issues"
              className="inline-flex items-center gap-1 rounded-md border border-border bg-surface px-3 py-2 text-sm text-text hover:bg-background"
            >
              <ListChecks className="h-4 w-4" aria-hidden="true" /> Issues
            </Link>
            <Link
              to="/app/meetings"
              className="inline-flex items-center gap-1 rounded-md border border-border bg-surface px-3 py-2 text-sm text-text hover:bg-background"
            >
              <CalendarDays className="h-4 w-4" aria-hidden="true" /> Meetings
            </Link>
          </div>
        }
      />

      {summary.isError ? (
        <InlineError error={summary.error} />
      ) : (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          <StatCard label="Open" value={summary.data?.open_count ?? 0} to="/app/issues?status=OPEN" />
          <StatCard
            label="In Progress"
            value={summary.data?.in_progress_count ?? 0}
            to="/app/issues?status=IN_PROGRESS"
          />
          <StatCard
            label="Pending"
            value={summary.data?.pending_count ?? 0}
            to="/app/issues?status=PENDING"
          />
          <StatCard
            label="Overdue"
            value={summary.data?.overdue_count ?? 0}
            to="/app/monitoring/overdue"
            tone="danger"
          />
          <StatCard
            label="Stagnant"
            value={summary.data?.stagnant_count ?? 0}
            to="/app/monitoring/stagnant"
            tone="warning"
          />
          <StatCard
            label="Due this week"
            value={summary.data?.due_this_week_count ?? 0}
            to="/app/monitoring/due-this-week"
            tone="warning"
          />
          <StatCard label="Active total" value={summary.data?.total_active_count ?? 0} />
        </div>
      )}

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <div>
          <h2 className="mb-2 text-sm font-semibold text-text">Recently updated issues</h2>
          <DataState
            isLoading={recent.isLoading}
            error={recent.error}
            isEmpty={(recent.data?.length ?? 0) === 0}
            loadingLabel="Loading issues…"
            emptyTitle="No recently updated issues"
          >
            <div className="space-y-2">
              {recent.data?.map((issue) => <IssueRow key={issue.id} issue={issue} />)}
            </div>
          </DataState>
        </div>

        <div>
          <h2 className="mb-2 text-sm font-semibold text-text">Recent meetings</h2>
          <DataState
            isLoading={meetings.isLoading}
            error={meetings.error}
            isEmpty={(meetings.data?.items.length ?? 0) === 0}
            loadingLabel="Loading meetings…"
            emptyTitle="No meetings recorded yet"
          >
            <div className="space-y-2">
              {meetings.data?.items.map((occ) => (
                <MeetingCard key={occ.id} occurrence={occ} typeName={typeName.get(occ.meeting_id)} />
              ))}
            </div>
          </DataState>
        </div>
      </div>

      <h2 className="mb-3 mt-8 text-base font-semibold text-text">Analytics</h2>
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="rounded-lg border border-border bg-surface p-4">
          <h3 className="mb-3 text-sm font-semibold text-text">Issues by category</h3>
          <DataState
            isLoading={byCategory.isLoading}
            error={byCategory.error}
            isEmpty={(byCategory.data?.length ?? 0) === 0}
            loadingLabel="Loading…"
            emptyTitle="No category data"
          >
            {byCategory.data && <DistributionBars data={byCategory.data} />}
          </DataState>
        </div>

        <div className="rounded-lg border border-border bg-surface p-4">
          <h3 className="mb-3 text-sm font-semibold text-text">Issues by responsible party</h3>
          <DataState
            isLoading={byResponsibleParty.isLoading}
            error={byResponsibleParty.error}
            isEmpty={(byResponsibleParty.data?.length ?? 0) === 0}
            loadingLabel="Loading…"
            emptyTitle="No responsible-party data"
          >
            {byResponsibleParty.data && <DistributionBars data={byResponsibleParty.data} />}
          </DataState>
        </div>

        <div className="rounded-lg border border-border bg-surface p-4">
          <div className="mb-3 flex items-center justify-between gap-2">
            <h3 className="text-sm font-semibold text-text">Opened vs closed</h3>
            <label className="text-xs text-muted">
              <span className="sr-only">Trend period in months</span>
              <select
                value={months}
                onChange={(e) => setMonths(Number(e.target.value))}
                aria-label="Trend period (months)"
                className="rounded border border-border bg-surface px-2 py-1 text-xs text-text"
              >
                {TREND_MONTHS.map((m) => (
                  <option key={m} value={m}>
                    {m} months
                  </option>
                ))}
              </select>
            </label>
          </div>
          <DataState
            isLoading={trend.isLoading}
            error={trend.error}
            isEmpty={(trend.data?.length ?? 0) === 0}
            loadingLabel="Loading…"
            emptyTitle="No trend data"
          >
            {trend.data && <TrendTable data={trend.data} />}
          </DataState>
        </div>
      </div>
    </section>
  );
}
