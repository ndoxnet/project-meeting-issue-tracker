// Concept by MrHan (08974747477)
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { usePageTitle } from '@/hooks/usePageTitle';
import { PageHeader } from '@/components/layout/PageHeader';
import { ExportCsvButton } from '@/features/reports/ExportCsvButton';
import type { IssueFilters } from '@/api/issues';

export function ReportsPage() {
  usePageTitle('Reports');
  const [includeArchived, setIncludeArchived] = useState(false);
  const [overdueOnly, setOverdueOnly] = useState(false);
  const [stagnantOnly, setStagnantOnly] = useState(false);

  const filters: IssueFilters = {
    include_archived: includeArchived || undefined,
    overdue: overdueOnly || undefined,
    stagnant: stagnantOnly || undefined,
  };

  return (
    <section>
      <PageHeader
        title="Reports & Export"
        description="Export the issue register to CSV for offline analysis."
      />

      <div className="max-w-xl space-y-4 rounded-lg border border-border bg-surface p-4">
        <p className="text-sm text-text">
          Choose optional filters, then export. For a precise, fully-filtered export (by status,
          priority, category, search, dates), open the{' '}
          <Link to="/app/issues" className="text-primary underline">
            Issue Register
          </Link>{' '}
          and use its <span className="font-medium">Export CSV</span> button — it reuses your active
          filters exactly.
        </p>

        <fieldset className="space-y-2">
          <legend className="text-sm font-medium text-text">Export filters</legend>
          <label className="flex items-center gap-2 text-sm text-text">
            <input
              type="checkbox"
              checked={overdueOnly}
              onChange={(e) => setOverdueOnly(e.target.checked)}
            />
            Overdue issues only
          </label>
          <label className="flex items-center gap-2 text-sm text-text">
            <input
              type="checkbox"
              checked={stagnantOnly}
              onChange={(e) => setStagnantOnly(e.target.checked)}
            />
            Stagnant issues only
          </label>
          <label className="flex items-center gap-2 text-sm text-text">
            <input
              type="checkbox"
              checked={includeArchived}
              onChange={(e) => setIncludeArchived(e.target.checked)}
            />
            Include archived issues
          </label>
        </fieldset>

        <div className="flex items-center gap-3">
          <ExportCsvButton filters={filters} label="Export issues to CSV" />
          <span className="text-xs text-muted">Large exports (over 10,000 rows) are rejected.</span>
        </div>
      </div>
    </section>
  );
}
