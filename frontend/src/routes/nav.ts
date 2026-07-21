// Concept by MrHan (08974747477)
// Sidebar navigation definition. `roles` gates visibility; the backend remains
// the source of truth for authorization (Phase 2).
import type { UserRole } from '@/types';

export interface NavItem {
  label: string;
  path: string;
  roles?: UserRole[]; // undefined = visible to all roles
}

export const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard', path: '/' },
  { label: 'Issues', path: '/issues' },
  { label: 'Meetings', path: '/meetings' },
  { label: 'Overdue', path: '/overdue' },
  { label: 'Reports', path: '/reports' },
  { label: 'Master Data', path: '/master-data', roles: ['ADMIN'] },
  { label: 'Users', path: '/users', roles: ['ADMIN'] },
  { label: 'Audit Log', path: '/audit-log', roles: ['ADMIN'] },
  { label: 'Settings', path: '/settings', roles: ['ADMIN'] },
];
