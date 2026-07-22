// Concept by MrHan (08974747477)
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from './useAuth';
import type { UserRole } from '@/api/types';

/**
 * Gates nested routes by role. UX only — the backend remains authoritative; a
 * hidden route is never a security control.
 */
export function RoleRoute({ allowedRoles }: { allowedRoles: UserRole[] }) {
  const { user } = useAuth();
  if (!user || !allowedRoles.includes(user.role)) {
    return <Navigate to="/forbidden" replace />;
  }
  return <Outlet />;
}
