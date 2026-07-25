// Concept by MrHan (08974747477)
import { useMutation } from '@tanstack/react-query';
import { apiClient } from './client';
import { triggerBrowserDownload } from '@/lib/download';
import type { IssueFilters } from './issues';

/**
 * The CSV export endpoint (`reports_issues_csv`) accepts a SUBSET of the issue
 * register's server-side filters. It exposes NO pagination or sort parameters,
 * so we deliberately send neither — the export must not be silently truncated by
 * a page size, and there is no contract-exposed sort to preserve. Every filter
 * below is passed through exactly as the register set it.
 */
export function issueFiltersToCsvQuery(
  filters: IssueFilters,
): Record<string, string | number | boolean | (string | number)[] | undefined> {
  return {
    search: filters.search || undefined,
    status: filters.status && filters.status.length ? filters.status : undefined,
    priority: filters.priority,
    category_id: filters.category_id,
    responsible_party_id: filters.responsible_party_id,
    pic_user_id: filters.pic_user_id,
    raised_date_from: filters.raised_date_from,
    raised_date_to: filters.raised_date_to,
    due_date_from: filters.due_date_from,
    due_date_to: filters.due_date_to,
    overdue: filters.overdue,
    stagnant: filters.stagnant,
    include_archived: filters.include_archived,
  };
}

const DEFAULT_CSV_FILENAME = 'issues.csv';

/** Download the issues register as CSV using the active filters. */
export async function exportIssuesCsv(filters: IssueFilters): Promise<void> {
  const { blob, filename } = await apiClient.download('/reports/issues.csv', {
    query: issueFiltersToCsvQuery(filters),
  });
  triggerBrowserDownload(blob, filename ?? DEFAULT_CSV_FILENAME);
}

export function useExportIssuesCsv() {
  return useMutation({ mutationFn: (filters: IssueFilters) => exportIssuesCsv(filters) });
}
