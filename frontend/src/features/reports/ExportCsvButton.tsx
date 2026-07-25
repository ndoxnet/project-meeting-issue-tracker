// Concept by MrHan (08974747477)
import { Download } from 'lucide-react';
import { ApiError } from '@/api/errors';
import { useExportIssuesCsv } from '@/api/reports';
import type { IssueFilters } from '@/api/issues';
import { useToast } from '@/components/feedback/ToastProvider';
import { Button } from '@/components/ui/Button';

/** Map an export failure to a plain-text message. */
export function exportErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.code === 'EXPORT_LIMIT_EXCEEDED') {
      return error.message || 'The export is too large. Narrow the filters and try again.';
    }
    return error.message;
  }
  return 'Export failed. Please try again.';
}

/** Export the issue register to CSV using the supplied (active) filters. */
export function ExportCsvButton({
  filters,
  label = 'Export CSV',
}: {
  filters: IssueFilters;
  label?: string;
}) {
  const toast = useToast();
  const exportCsv = useExportIssuesCsv();

  function onClick() {
    exportCsv.mutate(filters, {
      onSuccess: () => toast.success('CSV downloaded.'),
      onError: (err) => toast.error(exportErrorMessage(err)),
    });
  }

  return (
    <Button type="button" variant="secondary" loading={exportCsv.isPending} onClick={onClick}>
      <Download className="h-4 w-4" aria-hidden="true" /> {label}
    </Button>
  );
}
