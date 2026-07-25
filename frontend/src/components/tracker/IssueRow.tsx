// Concept by MrHan (08974747477)
import { Link } from 'react-router-dom';
import { Clock } from 'lucide-react';
import type { IssueListItem } from '@/api/types';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { PriorityBadge } from '@/components/ui/PriorityBadge';
import { formatDate } from '@/lib/dates';

/** Compact issue summary row linking to the issue detail. */
export function IssueRow({ issue }: { issue: IssueListItem }) {
  return (
    <Link
      to={`/app/issues/${issue.id}`}
      className="block rounded-lg border border-border bg-surface p-3 transition hover:border-primary/40"
    >
      <div className="flex flex-wrap items-center gap-2">
        <span className="font-mono text-xs text-muted">{issue.issue_code}</span>
        <StatusBadge status={issue.status} />
        <PriorityBadge priority={issue.priority} />
        {issue.is_overdue && (
          <span className="inline-flex items-center gap-1 rounded-full border border-red-200 bg-red-50 px-2 py-0.5 text-xs font-medium text-red-700">
            <Clock className="h-3 w-3" aria-hidden="true" />
            Overdue
          </span>
        )}
      </div>
      <p className="mt-1 font-medium text-text">{issue.title}</p>
      <div className="mt-1 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted">
        <span>Category: {issue.category_name ?? '—'}</span>
        <span>PIC: {issue.pic_name ?? '—'}</span>
        <span>Due: {formatDate(issue.due_date)}</span>
        <span>Last update: {issue.days_since_last_update}d ago</span>
      </div>
    </Link>
  );
}
