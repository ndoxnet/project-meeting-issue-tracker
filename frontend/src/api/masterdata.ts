// Concept by MrHan (08974747477)
import { useQuery } from '@tanstack/react-query';
import { apiClient } from './client';
import { queryKeys } from './queryKeys';
import type { NamedResponse, Page } from './types';

// Master data is small; fetch active items with a large page size for pickers.
const ACTIVE_PARAMS = { is_active: true, page: 1, page_size: 200 };

export function listCategories(): Promise<Page<NamedResponse>> {
  return apiClient.get<Page<NamedResponse>>('/categories', { query: ACTIVE_PARAMS });
}

export function listResponsibleParties(): Promise<Page<NamedResponse>> {
  return apiClient.get<Page<NamedResponse>>('/responsible-parties', { query: ACTIVE_PARAMS });
}

export function listMeetingTypes(): Promise<Page<NamedResponse>> {
  return apiClient.get<Page<NamedResponse>>('/meetings', { query: ACTIVE_PARAMS });
}

export function useCategories() {
  return useQuery({
    queryKey: queryKeys.master.categories,
    queryFn: listCategories,
    staleTime: 5 * 60_000,
  });
}

export function useResponsibleParties() {
  return useQuery({
    queryKey: queryKeys.master.responsibleParties,
    queryFn: listResponsibleParties,
    staleTime: 5 * 60_000,
  });
}

export function useMeetingTypes() {
  return useQuery({
    queryKey: queryKeys.meetings.types,
    queryFn: listMeetingTypes,
    staleTime: 5 * 60_000,
  });
}
