// Concept by MrHan (08974747477)
import { Link } from 'react-router-dom';
import { CalendarDays } from 'lucide-react';
import type { MeetingOccurrence } from '@/api/types';
import { formatDate } from '@/lib/dates';

/** Meeting-occurrence summary card. `typeName` is resolved from the meeting type. */
export function MeetingCard({
  occurrence,
  typeName,
}: {
  occurrence: MeetingOccurrence;
  typeName?: string;
}) {
  return (
    <Link
      to={`/app/meetings/${occurrence.id}`}
      className="block rounded-lg border border-border bg-surface p-4 transition hover:border-primary/40"
    >
      <div className="flex items-center gap-2 text-sm text-muted">
        <CalendarDays className="h-4 w-4" aria-hidden="true" />
        {formatDate(occurrence.meeting_date)}
        {occurrence.meeting_number && <span>· {occurrence.meeting_number}</span>}
      </div>
      <p className="mt-1 font-medium text-text">{typeName ?? 'Meeting'}</p>
      {occurrence.reference_number && (
        <p className="mt-1 text-xs text-muted">Ref: {occurrence.reference_number}</p>
      )}
      {occurrence.agenda && (
        <p className="mt-1 line-clamp-2 text-sm text-muted">{occurrence.agenda}</p>
      )}
    </Link>
  );
}
