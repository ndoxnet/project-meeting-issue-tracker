// Concept by MrHan (08974747477)
// User administration (ADMIN only — backend authoritative). All fetchers derive
// their request/response types from the generated schema.
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';
import { queryKeys } from './queryKeys';
import type {
  Message,
  Page,
  PasswordResetRequest,
  UserCreate,
  UserResponse,
  UserUpdate,
} from './types';

export interface UserFilters {
  page?: number;
  page_size?: number;
  search?: string;
  is_active?: boolean;
}

// ---- fetchers ----
export function listUsers(filters: UserFilters): Promise<Page<UserResponse>> {
  return apiClient.get<Page<UserResponse>>('/users', {
    query: {
      page: filters.page ?? 1,
      page_size: filters.page_size ?? 20,
      search: filters.search || undefined,
      is_active: filters.is_active,
    },
  });
}

export function createUser(body: UserCreate): Promise<UserResponse> {
  return apiClient.post<UserResponse>('/users', { json: body });
}

export function updateUser(id: string, body: UserUpdate): Promise<UserResponse> {
  return apiClient.patch<UserResponse>(`/users/${id}`, { json: body });
}

export function activateUser(id: string): Promise<UserResponse> {
  return apiClient.post<UserResponse>(`/users/${id}/activate`);
}

export function deactivateUser(id: string): Promise<UserResponse> {
  return apiClient.post<UserResponse>(`/users/${id}/deactivate`);
}

export function resetUserPassword(id: string, body: PasswordResetRequest): Promise<Message> {
  return apiClient.post<Message>(`/users/${id}/reset-password`, { json: body });
}

// ---- hooks ----
export function useUsers(filters: UserFilters) {
  return useQuery({
    queryKey: queryKeys.users.list(filters),
    queryFn: () => listUsers(filters),
  });
}

function useInvalidateUsers() {
  const qc = useQueryClient();
  return () => qc.invalidateQueries({ queryKey: ['users'] });
}

export function useCreateUser() {
  const invalidate = useInvalidateUsers();
  return useMutation({ mutationFn: (body: UserCreate) => createUser(body), onSuccess: invalidate });
}

export function useUpdateUser(id: string) {
  const invalidate = useInvalidateUsers();
  return useMutation({
    mutationFn: (body: UserUpdate) => updateUser(id, body),
    onSuccess: invalidate,
  });
}

export function useActivateUser() {
  const invalidate = useInvalidateUsers();
  return useMutation({ mutationFn: (id: string) => activateUser(id), onSuccess: invalidate });
}

export function useDeactivateUser() {
  const invalidate = useInvalidateUsers();
  return useMutation({ mutationFn: (id: string) => deactivateUser(id), onSuccess: invalidate });
}

export function useResetUserPassword(id: string) {
  return useMutation({ mutationFn: (body: PasswordResetRequest) => resetUserPassword(id, body) });
}
