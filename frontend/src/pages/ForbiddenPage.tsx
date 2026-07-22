// Concept by MrHan (08974747477)
import { Link } from 'react-router-dom';
import { usePageTitle } from '@/hooks/usePageTitle';

export function ForbiddenPage() {
  usePageTitle('Access denied');
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
      <p className="text-4xl font-bold text-muted">403</p>
      <h1 className="mt-2 text-lg font-semibold text-text">Access denied</h1>
      <p className="mt-1 max-w-sm text-sm text-muted">
        Your role does not have permission to view this page.
      </p>
      <Link to="/app/dashboard" className="mt-4 text-sm text-primary hover:underline">
        Back to Dashboard
      </Link>
    </div>
  );
}
