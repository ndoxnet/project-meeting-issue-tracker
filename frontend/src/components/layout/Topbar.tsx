// Concept by MrHan (08974747477)
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Menu, LogOut } from 'lucide-react';
import { useAuth } from '@/auth/useAuth';
import { RoleBadge } from '@/components/ui/RoleBadge';
import { Button } from '@/components/ui/Button';
import { env } from '@/config/env';

export function Topbar({ onOpenMenu }: { onOpenMenu: () => void }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [loggingOut, setLoggingOut] = useState(false);

  async function handleLogout() {
    setLoggingOut(true);
    await logout();
    navigate('/login', { replace: true });
  }

  return (
    <header className="flex h-14 items-center gap-3 border-b border-border bg-surface px-3 md:px-4">
      <button
        type="button"
        onClick={onOpenMenu}
        aria-label="Open navigation menu"
        className="rounded-md p-2 text-muted hover:bg-background md:hidden"
      >
        <Menu className="h-5 w-5" aria-hidden="true" />
      </button>

      <div className="font-semibold text-text">{env.appName}</div>

      <div className="ml-auto flex items-center gap-3">
        {user && (
          <div className="hidden items-center gap-2 sm:flex">
            <span className="text-sm text-text">{user.full_name}</span>
            <RoleBadge role={user.role} />
          </div>
        )}
        <Button
          variant="secondary"
          onClick={handleLogout}
          loading={loggingOut}
          aria-label="Log out"
        >
          <LogOut className="h-4 w-4" aria-hidden="true" />
          <span className="hidden sm:inline">Logout</span>
        </Button>
      </div>
    </header>
  );
}
