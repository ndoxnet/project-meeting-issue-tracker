// Concept by MrHan (08974747477)
import { AlertCircle } from 'lucide-react';
import type { IssuePriority } from '@/api/types';
import { cn } from '@/lib/cn';

const styles: Record<IssuePriority, string> = {
  LOW: 'border-slate-200 bg-slate-50 text-slate-600',
  MEDIUM: 'border-blue-200 bg-blue-50 text-blue-700',
  HIGH: 'border-orange-200 bg-orange-50 text-orange-700',
  CRITICAL: 'border-red-200 bg-red-50 text-red-700',
};
const label: Record<IssuePriority, string> = {
  LOW: 'Low',
  MEDIUM: 'Medium',
  HIGH: 'High',
  CRITICAL: 'Critical',
};

export function PriorityBadge({
  priority,
  className,
}: {
  priority: IssuePriority;
  className?: string;
}) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium',
        styles[priority],
        className,
      )}
    >
      {priority === 'CRITICAL' && <AlertCircle className="h-3 w-3" aria-hidden="true" />}
      {label[priority]}
    </span>
  );
}
