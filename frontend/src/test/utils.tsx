// Concept by MrHan (08974747477)
import type { ReactElement, ReactNode } from 'react';
import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { AuthContext } from '@/auth/AuthContext';
import { AuthProvider } from '@/auth/AuthProvider';
import { createQueryClient } from '@/api/queryClient';
import type { AuthContextValue, CurrentUser } from '@/auth/authTypes';
import { makeUser } from './handlers';
import type { UserRole } from '@/api/types';

/** A fully-formed fake auth context for guard/nav tests. */
export function fakeAuth(overrides: Partial<AuthContextValue> = {}): AuthContextValue {
  const user: CurrentUser | null = overrides.user ?? null;
  return {
    status: user ? 'authenticated' : 'unauthenticated',
    user,
    login: async () => {},
    logout: async () => {},
    refreshCurrentUser: async () => {},
    hasRole: (...roles: UserRole[]) => (user ? roles.includes(user.role) : false),
    ...overrides,
  };
}

export function authedAs(role: UserRole): AuthContextValue {
  return fakeAuth({ user: makeUser(role), status: 'authenticated' });
}

/** Render with a fixed (fake) auth context + MemoryRouter. */
export function renderWithAuth(
  ui: ReactElement,
  { value, initialEntries = ['/'] }: { value: AuthContextValue; initialEntries?: string[] },
) {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <AuthContext.Provider value={value}>{ui}</AuthContext.Provider>
    </MemoryRouter>,
  );
}

/** Render with the REAL AuthProvider (uses MSW) + query client + MemoryRouter. */
export function renderWithRealAuth(
  ui: ReactElement,
  { initialEntries = ['/'] }: { initialEntries?: string[] } = {},
) {
  const queryClient = createQueryClient();
  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <MemoryRouter initialEntries={initialEntries}>{children}</MemoryRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
  return { queryClient, ...render(ui, { wrapper }) };
}
