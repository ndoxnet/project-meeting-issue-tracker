// Concept by MrHan (08974747477)
// Application shell: sidebar navigation + top bar. Responsive (sidebar collapses
// on small screens). Phase 1 uses a static demo role for menu gating.
import { NavLink, Outlet } from 'react-router-dom';
import { NAV_ITEMS } from '@/routes/nav';
import type { UserRole } from '@/types';

// Phase 3 replaces this with the authenticated user's role.
const DEMO_ROLE: UserRole = 'ADMIN';

export default function AppShell() {
  const items = NAV_ITEMS.filter(
    (i) => !i.roles || i.roles.includes(DEMO_ROLE),
  );

  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside className="hidden w-56 shrink-0 border-r border-slate-200 bg-white md:block">
        <div className="px-4 py-4 text-sm font-semibold text-slate-800">
          Issue Tracker
        </div>
        <nav className="px-2">
          {items.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) =>
                `block rounded-md px-3 py-2 text-sm ${
                  isActive
                    ? 'bg-blue-50 font-medium text-blue-700'
                    : 'text-slate-600 hover:bg-slate-100'
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 items-center justify-between border-b border-slate-200 bg-white px-4">
          <span className="text-sm text-slate-500 md:hidden">Issue Tracker</span>
          <div className="ml-auto flex items-center gap-3">
            <span className="text-sm text-slate-600">Admin</span>
            <button className="rounded-md border border-slate-300 px-3 py-1 text-sm text-slate-600 hover:bg-slate-50">
              Logout
            </button>
          </div>
        </header>

        <main className="flex-1 p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
