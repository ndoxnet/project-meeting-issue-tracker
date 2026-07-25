// Concept by MrHan (08974747477)
// Admin CRUD for the three "named" master-data resources (categories,
// responsible parties, meeting types). All three share NamedCreate/NamedUpdate/
// NamedResponse and identical endpoint shapes, so they are handled generically.
// Mutations require ADMIN (backend authoritative); list/get are open to any role.
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';
import { queryKeys } from './queryKeys';
import type { NamedCreate, NamedResponse, NamedUpdate, Page } from './types';

export type NamedResourceKind = 'categories' | 'responsible-parties' | 'meetings';

/** URL path segment per kind. */
const PATH: Record<NamedResourceKind, string> = {
  categories: '/categories',
  'responsible-parties': '/responsible-parties',
  meetings: '/meetings',
};

/** The active-only picker query key that each kind feeds, so edits refresh it. */
const PICKER_KEY: Record<NamedResourceKind, readonly unknown[]> = {
  categories: queryKeys.master.categories,
  'responsible-parties': queryKeys.master.responsibleParties,
  meetings: queryKeys.meetings.types,
};

export interface NamedListFilters {
  /** Omit to list ALL; true/false to filter by active state (contract param). */
  is_active?: boolean;
  search?: string;
  page?: number;
  page_size?: number;
}

// ---- fetchers ----
export function listNamed(
  kind: NamedResourceKind,
  filters: NamedListFilters = {},
): Promise<Page<NamedResponse>> {
  return apiClient.get<Page<NamedResponse>>(PATH[kind], {
    query: {
      page: filters.page ?? 1,
      page_size: filters.page_size ?? 50,
      is_active: filters.is_active,
      search: filters.search || undefined,
    },
  });
}

export function createNamed(kind: NamedResourceKind, body: NamedCreate): Promise<NamedResponse> {
  return apiClient.post<NamedResponse>(PATH[kind], { json: body });
}

export function updateNamed(
  kind: NamedResourceKind,
  id: string,
  body: NamedUpdate,
): Promise<NamedResponse> {
  return apiClient.patch<NamedResponse>(`${PATH[kind]}/${id}`, { json: body });
}

export function activateNamed(kind: NamedResourceKind, id: string): Promise<NamedResponse> {
  return apiClient.post<NamedResponse>(`${PATH[kind]}/${id}/activate`);
}

export function deactivateNamed(kind: NamedResourceKind, id: string): Promise<NamedResponse> {
  return apiClient.post<NamedResponse>(`${PATH[kind]}/${id}/deactivate`);
}

// ---- hooks ----
export function useNamedList(kind: NamedResourceKind, filters: NamedListFilters) {
  return useQuery({
    queryKey: queryKeys.master.adminList(kind, filters),
    queryFn: () => listNamed(kind, filters),
  });
}

function useInvalidateNamed(kind: NamedResourceKind) {
  const qc = useQueryClient();
  return () => {
    // The management lists for this kind…
    qc.invalidateQueries({ queryKey: ['master-admin', kind] });
    // …the active-only picker that new records use…
    qc.invalidateQueries({ queryKey: PICKER_KEY[kind] });
    // …and dashboard analytics, whose labels/counts derive from master data.
    qc.invalidateQueries({ queryKey: ['dashboard'] });
  };
}

export function useCreateNamed(kind: NamedResourceKind) {
  const invalidate = useInvalidateNamed(kind);
  return useMutation({
    mutationFn: (body: NamedCreate) => createNamed(kind, body),
    onSuccess: invalidate,
  });
}

export function useUpdateNamed(kind: NamedResourceKind) {
  const invalidate = useInvalidateNamed(kind);
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: NamedUpdate }) => updateNamed(kind, id, body),
    onSuccess: invalidate,
  });
}

export function useActivateNamed(kind: NamedResourceKind) {
  const invalidate = useInvalidateNamed(kind);
  return useMutation({
    mutationFn: (id: string) => activateNamed(kind, id),
    onSuccess: invalidate,
  });
}

export function useDeactivateNamed(kind: NamedResourceKind) {
  const invalidate = useInvalidateNamed(kind);
  return useMutation({
    mutationFn: (id: string) => deactivateNamed(kind, id),
    onSuccess: invalidate,
  });
}
