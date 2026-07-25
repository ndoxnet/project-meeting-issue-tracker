// Concept by MrHan (08974747477)
import type { IssueStatus } from '@/api/types';
import { cn } from '@/lib/cn';

// Built-in Tailwind palette (always generated). Text label is always shown —
// never color-only.
const styles: Record<IssueStatus, string> = {
  OPEN: 'border-blue-200 bg-blue-50 text-blue-700',
  IN_PROGRESS: 'border-cyan-200 bg-cyan-50 text-cyan-700',
  PENDING: 'border-amber-200 bg-amber-50 text-amber-700',
  CLOSED: 'border-green-200 bg-green-50 text-green-700',
  REOPENED: 'border-violet-200 bg-violet-50 text-violet-700',
};
const label: Record<IssueStatus, string> = {
  OPEN: 'Open',
  IN_PROGRESS: 'In Progress',
  PENDING: 'Pending',
  CLOSED: 'Closed',
  REOPENED: 'Reopened',
};

export function StatusBadge({ status, className }: { status: IssueStatus; className?: string }) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium',
        styles[status],
        className,
      )}
    >
      {label[status]}
    </span>
  );
}
