// Concept by MrHan (08974747477)
import type { CurrentUser, LoginInput, UserRole } from '@/api/types';

export type AuthStatus =
  | 'idle'
  | 'checking'
  | 'authenticating'
  | 'authenticated'
  | 'unauthenticated';

export interface AuthContextValue {
  status: AuthStatus;
  user: CurrentUser | null;
  login(input: LoginInput): Promise<void>;
  logout(): Promise<void>;
  refreshCurrentUser(): Promise<void>;
  hasRole(...roles: UserRole[]): boolean;
  // NOTE: the access token is intentionally NOT exposed here (ADR-017).
}

export type { CurrentUser, LoginInput, UserRole };
