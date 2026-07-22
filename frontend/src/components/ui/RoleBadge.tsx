// Concept by MrHan (08974747477)
import type { UserRole } from '@/api/types';
import { cn } from '@/lib/cn';

const label: Record<UserRole, string> = { ADMIN: 'Admin', EDITOR: 'Editor', VIEWER: 'Viewer' };

/** Text badge for a role (color is not the only indicator — the text is shown). */
export function RoleBadge({ role, className }: { role: UserRole; className?: string }) {
  return (
    <span
      className={cn(
        'rounded-full border border-border bg-background px-2 py-0.5 text-xs font-medium text-muted',
        className,
      )}
    >
      {label[role]}
    </span>
  );
}
