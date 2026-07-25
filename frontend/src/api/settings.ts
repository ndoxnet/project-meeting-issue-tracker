// Concept by MrHan (08974747477)
// Read-only application settings. Phase 2C.4B intentionally does NOT expose an
// update path: runtime configuration currently comes from environment config,
// not the app_settings table (see the governance review).
import { useQuery } from '@tanstack/react-query';
import { apiClient } from './client';
import { queryKeys } from './queryKeys';
import type { AppSettingResponse } from './types';

export function listSettings(): Promise<AppSettingResponse[]> {
  return apiClient.get<AppSettingResponse[]>('/settings');
}

export function useSettings() {
  return useQuery({ queryKey: queryKeys.settings.all, queryFn: listSettings });
}
