// Concept by MrHan (08974747477)
import { NavLink } from 'react-router-dom';
import { visibleNavItems } from '@/components/navigation/navigation';
import { useAuth } from '@/auth/useAuth';
import { cn } from '@/lib/cn';

/** Sidebar nav list, reused by the desktop rail and the mobile drawer. */
export function SidebarNav({ onNavigate }: { onNavigate?: () => void }) {
  const { user } = useAuth();
  const items = visibleNavItems(user?.role);

  return (
    <nav aria-label="Primary" className="px-2 py-2">
      <ul className="space-y-1">
        {items.map(({ label, to, icon: Icon }) => (
          <li key={to}>
            <NavLink
              to={to}
              onClick={onNavigate}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-md px-3 py-2 text-sm',
                  isActive
                    ? 'bg-primary/10 font-medium text-primary'
                    : 'text-muted hover:bg-background hover:text-text',
                )
              }
              aria-current={undefined}
            >
              {({ isActive }) => (
                <>
                  <Icon className="h-4 w-4" aria-hidden="true" />
                  <span aria-current={isActive ? 'page' : undefined}>{label}</span>
                </>
              )}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}
