// Concept by MrHan (08974747477)
import { Link, Navigate, useParams } from 'react-router-dom';
import { usePageTitle } from '@/hooks/usePageTitle';
import { PageHeader } from '@/components/layout/PageHeader';
import { DataState } from '@/components/feedback/DataState';
import { IssueRow } from '@/components/tracker/IssueRow';
import { useMonitoringList, type MonitoringView } from '@/api/dashboard';

const MONITORING_LIMIT = 50;

const VIEWS: Record<
  MonitoringView,
  { title: string; description: string; registerHref: string | null }
> = {
  overdue: {
    title: 'Overdue issues',
    description: 'Active issues past their due date, most urgent first.',
    registerHref: '/app/issues?overdue=true',
  },
  stagnant: {
    title: 'Stagnant issues',
    description: 'Active issues with no recent follow-up.',
    registerHref: '/app/issues?stagnant=true',
  },
  'due-this-week': {
    title: 'Due this week',
    description: 'Active issues due within the next seven days.',
    registerHref: null,
  },
};

function isMonitoringView(value: string): value is MonitoringView {
  return value === 'overdue' || value === 'stagnant' || value === 'due-this-week';
}

export function MonitoringPage() {
  const { view = '' } = useParams();
  const meta = isMonitoringView(view) ? VIEWS[view] : null;
  usePageTitle(meta ? meta.title : 'Monitoring');

  // Hooks must run unconditionally; an invalid view falls back to a harmless key
  // and is redirected away below before anything is shown.
  const list = useMonitoringList(isMonitoringView(view) ? view : 'overdue', MONITORING_LIMIT);

  if (!meta) return <Navigate to="/app/dashboard" replace />;

  return (
    <section>
      <PageHeader title={meta.title} description={meta.description} backTo="/app/dashboard" />
      <DataState
        isLoading={list.isLoading}
        error={list.error}
        isEmpty={(list.data?.length ?? 0) === 0}
        loadingLabel="Loading issues…"
        emptyTitle="Nothing here right now"
        emptyDescription="No issues currently match this view."
      >
        <div className="space-y-2">
          {list.data?.map((issue) => <IssueRow key={issue.id} issue={issue} />)}
        </div>
        <p className="mt-3 text-xs text-muted">
          Showing up to {MONITORING_LIMIT} issues.{' '}
          {meta.registerHref && (
            <Link to={meta.registerHref} className="text-primary underline">
              Open the full filtered list in the register.
            </Link>
          )}
        </p>
      </DataState>
    </section>
  );
}
