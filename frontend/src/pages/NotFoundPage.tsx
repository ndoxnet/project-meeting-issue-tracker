// Concept by MrHan (08974747477)
import { Link } from 'react-router-dom';
import { usePageTitle } from '@/hooks/usePageTitle';

export function NotFoundPage() {
  usePageTitle('Not found');
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
      <p className="text-4xl font-bold text-muted">404</p>
      <h1 className="mt-2 text-lg font-semibold text-text">Page not found</h1>
      <Link to="/app/dashboard" className="mt-4 text-sm text-primary hover:underline">
        Back to Dashboard
      </Link>
    </div>
  );
}
