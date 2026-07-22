// Concept by MrHan (08974747477)
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from './useAuth';
import { LoadingScreen } from '@/components/feedback/LoadingScreen';

/** Gates nested routes behind authentication. Preserves the intended location. */
export function ProtectedRoute() {
  const { status } = useAuth();
  const location = useLocation();

  if (status === 'checking' || status === 'authenticating') {
    return <LoadingScreen label="Checking your session…" />;
  }
  if (status !== 'authenticated') {
    // Remember where the user was headed (validated on the login side).
    return <Navigate to="/login" replace state={{ from: location.pathname + location.search }} />;
  }
  return <Outlet />;
}
