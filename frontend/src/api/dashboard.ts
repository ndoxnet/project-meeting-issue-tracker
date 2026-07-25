// Concept by MrHan (08974747477)
import { useQuery } from '@tanstack/react-query';
import { apiClient } from './client';
import { queryKeys } from './queryKeys';
import type { DashboardSummary, IssueListItem } from './types';

export function getSummary(): Promise<DashboardSummary> {
  return apiClient.get<DashboardSummary>('/dashboard/summary');
}

export function getRecentlyUpdated(limit: number): Promise<IssueListItem[]> {
  return apiClient.get<IssueListItem[]>('/dashboard/recently-updated', { query: { limit } });
}

export function useDashboardSummary() {
  return useQuery({ queryKey: queryKeys.dashboard.summary, queryFn: getSummary });
}

export function useRecentlyUpdated(limit = 5) {
  return useQuery({
    queryKey: queryKeys.dashboard.recentlyUpdated(limit),
    queryFn: () => getRecentlyUpdated(limit),
  });
}
