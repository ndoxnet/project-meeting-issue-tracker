// Concept by MrHan (08974747477)
import { describe, expect, it } from 'vitest';
import { screen } from '@testing-library/react';
import { Route, Routes } from 'react-router-dom';
import { SidebarNav } from '@/components/layout/Sidebar';
import { visibleNavItems } from './navigation';
import { authedAs, renderWithAuth } from '@/test/utils';

const ADMIN_ONLY = ['Users', 'Audit', 'Settings'];
const COMMON = ['Dashboard', 'Issues', 'Meetings', 'Reports'];

describe('navigation config', () => {
  it('shows all menus to admin', () => {
    const labels = visibleNavItems('ADMIN').map((i) => i.label);
    expect(labels).toEqual(expect.arrayContaining([...COMMON, ...ADMIN_ONLY]));
  });

  it('hides admin menus from editor and viewer', () => {
    for (const role of ['EDITOR', 'VIEWER'] as const) {
      const labels = visibleNavItems(role).map((i) => i.label);
      expect(labels).toEqual(expect.arrayContaining(COMMON));
      ADMIN_ONLY.forEach((m) => expect(labels).not.toContain(m));
    }
  });
});

describe('SidebarNav rendering', () => {
  function render(role: 'ADMIN' | 'EDITOR' | 'VIEWER') {
    return renderWithAuth(
      <Routes>
        <Route path="/app/dashboard" element={<SidebarNav />} />
      </Routes>,
      { value: authedAs(role), initialEntries: ['/app/dashboard'] },
    );
  }

  it('renders admin-only links for admin', () => {
    render('ADMIN');
    expect(screen.getByRole('link', { name: /users/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /settings/i })).toBeInTheDocument();
  });

  it('omits admin-only links for editor', () => {
    render('EDITOR');
    expect(screen.queryByRole('link', { name: /users/i })).not.toBeInTheDocument();
    expect(screen.getByRole('link', { name: /issues/i })).toBeInTheDocument();
  });
});
