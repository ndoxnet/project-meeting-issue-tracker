// Concept by MrHan (08974747477)
import { useQuery } from '@tanstack/react-query';
import { apiClient } from './client';
import { queryKeys } from './queryKeys';
import type { CountByLabel, DashboardSummary, IssueListItem, MonthlyTrendPoint } from './types';

export function getSummary(): Promise<DashboardSummary> {
  return apiClient.get<DashboardSummary>('/dashboard/summary');
}

export function getRecentlyUpdated(limit: number): Promise<IssueListItem[]> {
  return apiClient.get<IssueListItem[]>('/dashboard/recently-updated', { query: { limit } });
}

// ---- monitoring lists (dedicated endpoints; logic stays server-side) ----
export type MonitoringView = 'overdue' | 'stagnant' | 'due-this-week';

export function getMonitoringList(view: MonitoringView, limit: number): Promise<IssueListItem[]> {
  return apiClient.get<IssueListItem[]>(`/dashboard/${view}`, { query: { limit } });
}

// ---- distributions & trend ----
export function getByCategory(): Promise<CountByLabel[]> {
  return apiClient.get<CountByLabel[]>('/dashboard/by-category');
}

export function getByResponsibleParty(): Promise<CountByLabel[]> {
  return apiClient.get<CountByLabel[]>('/dashboard/by-responsible-party');
}

export function getOpenedVsClosed(months: number): Promise<MonthlyTrendPoint[]> {
  return apiClient.get<MonthlyTrendPoint[]>('/dashboard/opened-vs-closed', { query: { months } });
}

// ---- hooks ----
export function useDashboardSummary() {
  return useQuery({ queryKey: queryKeys.dashboard.summary, queryFn: getSummary });
}

export function useRecentlyUpdated(limit = 5) {
  return useQuery({
    queryKey: queryKeys.dashboard.recentlyUpdated(limit),
    queryFn: () => getRecentlyUpdated(limit),
  });
}

const MONITORING_KEY = {
  overdue: (limit: number) => queryKeys.dashboard.overdue(limit),
  stagnant: (limit: number) => queryKeys.dashboard.stagnant(limit),
  'due-this-week': (limit: number) => queryKeys.dashboard.dueThisWeek(limit),
} as const;

export function useMonitoringList(view: MonitoringView, limit = 50) {
  return useQuery({
    queryKey: MONITORING_KEY[view](limit),
    queryFn: () => getMonitoringList(view, limit),
  });
}

export function useByCategory() {
  return useQuery({ queryKey: queryKeys.dashboard.byCategory, queryFn: getByCategory });
}

export function useByResponsibleParty() {
  return useQuery({
    queryKey: queryKeys.dashboard.byResponsibleParty,
    queryFn: getByResponsibleParty,
  });
}

export function useOpenedVsClosed(months: number) {
  return useQuery({
    queryKey: queryKeys.dashboard.openedVsClosed(months),
    queryFn: () => getOpenedVsClosed(months),
  });
}
