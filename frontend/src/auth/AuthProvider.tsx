// Concept by MrHan (08974747477)
import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { setUnauthorizedHandler } from '@/api/client';
import {
  clearAccessToken,
  setAccessToken,
} from './tokenStore';
import * as authApi from './authApi';
import { AuthContext } from './AuthContext';
import type { AuthContextValue, AuthStatus, CurrentUser, LoginInput, UserRole } from './authTypes';

export function AuthProvider({ children }: { children: ReactNode }) {
  // Memory-only token means the app always starts unauthenticated on load/refresh.
  const [status, setStatus] = useState<AuthStatus>('unauthenticated');
  const [user, setUser] = useState<CurrentUser | null>(null);
  const queryClient = useQueryClient();

  const clearSession = useCallback(() => {
    clearAccessToken();
    setUser(null);
    setStatus('unauthenticated');
    // Sensitive server data must not outlive the session.
    queryClient.clear();
  }, [queryClient]);

  // On any 401 from the API client, tear the session down. Route guards then
  // redirect to /login (no imperative navigation needed here).
  useEffect(() => {
    setUnauthorizedHandler(() => clearSession());
    return () => setUnauthorizedHandler(null);
  }, [clearSession]);

  const login = useCallback(async (input: LoginInput) => {
    setStatus('authenticating');
    try {
      const res = await authApi.login(input);
      setAccessToken(res.access_token); // memory only
      setUser(res.user);
      setStatus('authenticated');
    } catch (err) {
      clearSession();
      throw err;
    }
  }, [clearSession]);

  const logout = useCallback(async () => {
    try {
      await authApi.logout(); // best-effort; no server-side revocation (ADR-009)
    } catch {
      // Ignore backend failure — we always clear locally.
    } finally {
      clearSession();
    }
  }, [clearSession]);

  const refreshCurrentUser = useCallback(async () => {
    const me = await authApi.getCurrentUser();
    setUser(me);
    setStatus('authenticated');
  }, []);

  const hasRole = useCallback(
    (...roles: UserRole[]) => (user ? roles.includes(user.role) : false),
    [user],
  );

  const value = useMemo<AuthContextValue>(
    () => ({ status, user, login, logout, refreshCurrentUser, hasRole }),
    [status, user, login, logout, refreshCurrentUser, hasRole],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
