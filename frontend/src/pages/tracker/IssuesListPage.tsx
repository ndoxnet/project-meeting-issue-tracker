// Concept by MrHan (08974747477)
import { useSearchParams, Link } from 'react-router-dom';
import { Plus, Search } from 'lucide-react';
import { usePageTitle } from '@/hooks/usePageTitle';
import { PageHeader } from '@/components/layout/PageHeader';
import { DataState } from '@/components/feedback/DataState';
import { Pagination } from '@/components/ui/Pagination';
import { IssueRow } from '@/components/tracker/IssueRow';
import { Select, TextInput } from '@/components/ui/Field';
import { useAuth } from '@/auth/useAuth';
import { useIssues, type IssueFilters } from '@/api/issues';
import { useCategories } from '@/api/masterdata';
import { ISSUE_PRIORITIES, ISSUE_STATUSES, type IssueStatus } from '@/api/types';

export function IssuesListPage() {
  usePageTitle('Issues');
  const { hasRole } = useAuth();
  const [params, setParams] = useSearchParams();
  const categories = useCategories();

  const page = Number(params.get('page') ?? '1');
  const statusParam = params.get('status') ?? '';
  const filters: IssueFilters = {
    page,
    page_size: 20,
    search: params.get('search') ?? undefined,
    status: statusParam ? [statusParam as IssueStatus] : undefined,
    priority: (params.get('priority') as IssueFilters['priority']) ?? undefined,
    category_id: params.get('category_id') ?? undefined,
    overdue: params.get('overdue') === 'true' ? true : undefined,
  };
  const issues = useIssues(filters);

  // Update a filter param and reset to page 1 (page changes keep other params).
  function setFilter(key: string, value: string) {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value);
    else next.delete(key);
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
        title="Issue Register"
        description="All project issues raised across meetings."
        actions={
          hasRole('EDITOR', 'ADMIN') ? (
            <Link
              to="/app/issues/new"
              className="inline-flex items-center gap-1 rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-fg"
            >
              <Plus className="h-4 w-4" aria-hidden="true" /> New Issue
            </Link>
          ) : undefined
        }
      />

      <div className="mb-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-5">
        <label className="relative sm:col-span-2">
          <span className="sr-only">Search issues</span>
          <Search
            className="pointer-events-none absolute left-2 top-1/2 mt-0.5 h-4 w-4 -translate-y-1/2 text-muted"
            aria-hidden="true"
          />
          <TextInput
            defaultValue={params.get('search') ?? ''}
            placeholder="Search code, title, PIC…"
            className="mt-0 pl-8"
            onKeyDown={(e) => {
              if (e.key === 'Enter') setFilter('search', (e.target as HTMLInputElement).value);
            }}
            aria-label="Search issues"
          />
        </label>
        <Select
          value={statusParam}
          onChange={(e) => setFilter('status', e.target.value)}
          className="mt-0"
          aria-label="Filter by status"
        >
          <option value="">All statuses</option>
          {ISSUE_STATUSES.map((s) => (
            <option key={s} value={s}>
              {s.replace('_', ' ')}
            </option>
          ))}
        </Select>
        <Select
          value={params.get('priority') ?? ''}
          onChange={(e) => setFilter('priority', e.target.value)}
          className="mt-0"
          aria-label="Filter by priority"
        >
          <option value="">All priorities</option>
          {ISSUE_PRIORITIES.map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </Select>
        <Select
          value={params.get('category_id') ?? ''}
          onChange={(e) => setFilter('category_id', e.target.value)}
          className="mt-0"
          aria-label="Filter by category"
        >
          <option value="">All categories</option>
          {categories.data?.items.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </Select>
      </div>

      <label className="mb-3 flex items-center gap-2 text-sm text-muted">
        <input
          type="checkbox"
          checked={params.get('overdue') === 'true'}
          onChange={(e) => setFilter('overdue', e.target.checked ? 'true' : '')}
        />
        Overdue only
      </label>

      <DataState
        isLoading={issues.isLoading}
        error={issues.error}
        isEmpty={(issues.data?.items.length ?? 0) === 0}
        loadingLabel="Loading issues…"
        emptyTitle="No issues match your filters"
        emptyDescription="Try clearing filters or create a new issue."
      >
        <div className="space-y-2">
          {issues.data?.items.map((issue) => <IssueRow key={issue.id} issue={issue} />)}
        </div>
        {issues.data && <Pagination meta={issues.data.meta} onPageChange={setPage} />}
      </DataState>
    </section>
  );
}
