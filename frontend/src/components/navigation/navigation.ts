// Concept by MrHan (08974747477)
// Centralized navigation config. `roles` gates menu visibility; restricted routes
// are ALSO wrapped in <RoleRoute> (menu hiding is UX only).
import {
  LayoutDashboard,
  ListChecks,
  CalendarDays,
  FileText,
  Users,
  ScrollText,
  Settings,
  type LucideIcon,
} from 'lucide-react';
import type { UserRole } from '@/api/types';

export interface NavItem {
  label: string;
  to: string;
  icon: LucideIcon;
  roles?: UserRole[]; // undefined = visible to all authenticated roles
}

export const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard', to: '/app/dashboard', icon: LayoutDashboard },
  { label: 'Issues', to: '/app/issues', icon: ListChecks },
  { label: 'Meetings', to: '/app/meetings', icon: CalendarDays },
  { label: 'Reports', to: '/app/reports', icon: FileText },
  { label: 'Users', to: '/app/users', icon: Users, roles: ['ADMIN'] },
  { label: 'Audit', to: '/app/audit', icon: ScrollText, roles: ['ADMIN'] },
  { label: 'Settings', to: '/app/settings', icon: Settings, roles: ['ADMIN'] },
];

export function visibleNavItems(role: UserRole | undefined): NavItem[] {
  return NAV_ITEMS.filter((i) => !i.roles || (role && i.roles.includes(role)));
}
