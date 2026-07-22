// Concept by MrHan (08974747477)
import { describe, expect, it } from 'vitest';
import { screen } from '@testing-library/react';
import { Route, Routes } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import { RoleRoute } from './RoleRoute';
import { authedAs, fakeAuth, renderWithAuth } from '@/test/utils';

function tree() {
  return (
    <Routes>
      <Route path="/login" element={<div>Login Screen</div>} />
      <Route path="/forbidden" element={<div>Forbidden Screen</div>} />
      <Route element={<ProtectedRoute />}>
        <Route path="/app/dashboard" element={<div>Dashboard Content</div>} />
        <Route element={<RoleRoute allowedRoles={['ADMIN']} />}>
          <Route path="/app/users" element={<div>Users Admin</div>} />
        </Route>
      </Route>
    </Routes>
  );
}

describe('ProtectedRoute', () => {
  it('redirects unauthenticated users to /login', () => {
    renderWithAuth(tree(), { value: fakeAuth(), initialEntries: ['/app/dashboard'] });
    expect(screen.getByText('Login Screen')).toBeInTheDocument();
  });

  it('renders the child when authenticated', () => {
    renderWithAuth(tree(), { value: authedAs('EDITOR'), initialEntries: ['/app/dashboard'] });
    expect(screen.getByText('Dashboard Content')).toBeInTheDocument();
  });
});

describe('RoleRoute', () => {
  it('allows an admin to reach an admin route', () => {
    renderWithAuth(tree(), { value: authedAs('ADMIN'), initialEntries: ['/app/users'] });
    expect(screen.getByText('Users Admin')).toBeInTheDocument();
  });

  it('sends an editor to /forbidden', () => {
    renderWithAuth(tree(), { value: authedAs('EDITOR'), initialEntries: ['/app/users'] });
    expect(screen.getByText('Forbidden Screen')).toBeInTheDocument();
  });

  it('sends a viewer to /forbidden', () => {
    renderWithAuth(tree(), { value: authedAs('VIEWER'), initialEntries: ['/app/users'] });
    expect(screen.getByText('Forbidden Screen')).toBeInTheDocument();
  });
});
