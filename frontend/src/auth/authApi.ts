// Concept by MrHan (08974747477)
// Auth endpoint calls against the frozen v1 contract.
import { apiClient } from '@/api/client';
import type { CurrentUser, LoginInput, TokenResponse } from '@/api/types';

export function login(input: LoginInput): Promise<TokenResponse> {
  return apiClient.post<TokenResponse>('/auth/login', { json: input });
}

export function getCurrentUser(): Promise<CurrentUser> {
  return apiClient.get<CurrentUser>('/auth/me');
}

export function logout(): Promise<void> {
  return apiClient.post<void>('/auth/logout', { parse: 'void' });
}
