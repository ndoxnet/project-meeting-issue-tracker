// Concept by MrHan (08974747477)
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';
import { queryKeys } from './queryKeys';
import type {
  IssueCloseRequest,
  IssueCreate,
  IssueCreateResponse,
  IssueDetailResponse,
  IssueMetadataUpdate,
  IssuePriority,
  IssueReopenRequest,
  IssueStatus,
  IssueStatusChangeRequest,
  IssueUpdateCreate,
  IssueUpdateResponse,
  IssueUpdateVoidRequest,
  Page,
  IssueListItem,
  VoidResponse,
} from './types';

export interface IssueFilters {
  page?: number;
  page_size?: number;
  search?: string;
  status?: IssueStatus[];
  priority?: IssuePriority;
  category_id?: string;
  responsible_party_id?: string;
  pic_user_id?: string;
  pic_name?: string;
  meeting_id?: string;
  meeting_occurrence_id?: string;
  raised_date_from?: string;
  raised_date_to?: string;
  due_date_from?: string;
  due_date_to?: string;
  overdue?: boolean;
  stagnant?: boolean;
  include_archived?: boolean;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

// ---- fetchers ----
export function listIssues(filters: IssueFilters): Promise<Page<IssueListItem>> {
  return apiClient.get<Page<IssueListItem>>('/issues', {
    query: {
      page: filters.page ?? 1,
      page_size: filters.page_size ?? 20,
      search: filters.search || undefined,
      status: filters.status && filters.status.length ? filters.status : undefined,
      priority: filters.priority,
      category_id: filters.category_id,
      responsible_party_id: filters.responsible_party_id,
      pic_user_id: filters.pic_user_id,
      pic_name: filters.pic_name || undefined,
      meeting_id: filters.meeting_id,
      meeting_occurrence_id: filters.meeting_occurrence_id,
      raised_date_from: filters.raised_date_from,
      raised_date_to: filters.raised_date_to,
      due_date_from: filters.due_date_from,
      due_date_to: filters.due_date_to,
      overdue: filters.overdue,
      stagnant: filters.stagnant,
      include_archived: filters.include_archived,
      sort_by: filters.sort_by,
      sort_order: filters.sort_order,
    },
  });
}

export function getIssue(id: string): Promise<IssueDetailResponse> {
  return apiClient.get<IssueDetailResponse>(`/issues/${id}`);
}

export function listIssueUpdates(id: string): Promise<IssueUpdateResponse[]> {
  return apiClient.get<IssueUpdateResponse[]>(`/issues/${id}/updates`, {
    query: { order: 'asc' },
  });
}

export function createIssue(body: IssueCreate): Promise<IssueCreateResponse> {
  return apiClient.post<IssueCreateResponse>('/issues', { json: body });
}

export function updateIssue(id: string, body: IssueMetadataUpdate): Promise<IssueDetailResponse> {
  return apiClient.patch<IssueDetailResponse>(`/issues/${id}`, { json: body });
}

export function changeStatus(
  id: string,
  body: IssueStatusChangeRequest,
): Promise<IssueDetailResponse> {
  return apiClient.post<IssueDetailResponse>(`/issues/${id}/status`, { json: body });
}

export function closeIssue(id: string, body: IssueCloseRequest): Promise<IssueDetailResponse> {
  return apiClient.post<IssueDetailResponse>(`/issues/${id}/close`, { json: body });
}

export function reopenIssue(id: string, body: IssueReopenRequest): Promise<IssueDetailResponse> {
  return apiClient.post<IssueDetailResponse>(`/issues/${id}/reopen`, { json: body });
}

export function addFollowUp(id: string, body: IssueUpdateCreate): Promise<IssueUpdateResponse> {
  return apiClient.post<IssueUpdateResponse>(`/issues/${id}/updates`, { json: body });
}

export function voidUpdate(
  issueId: string,
  updateId: string,
  body: IssueUpdateVoidRequest,
): Promise<VoidResponse> {
  return apiClient.post<VoidResponse>(`/issues/${issueId}/updates/${updateId}/void`, { json: body });
}

// ---- query hooks ----
export function useIssues(filters: IssueFilters) {
  return useQuery({
    queryKey: queryKeys.issues.list(filters),
    queryFn: () => listIssues(filters),
  });
}

export function useIssue(id: string) {
  return useQuery({
    queryKey: queryKeys.issues.detail(id),
    queryFn: () => getIssue(id),
    enabled: !!id,
  });
}

export function useIssueUpdates(id: string) {
  return useQuery({
    queryKey: queryKeys.issues.updates(id),
    queryFn: () => listIssueUpdates(id),
    enabled: !!id,
  });
}

// ---- mutation hooks ----
function useInvalidateIssue(id?: string) {
  const qc = useQueryClient();
  return () => {
    qc.invalidateQueries({ queryKey: ['issues'] });
    qc.invalidateQueries({ queryKey: ['dashboard'] });
    if (id) {
      qc.invalidateQueries({ queryKey: queryKeys.issues.detail(id) });
      qc.invalidateQueries({ queryKey: queryKeys.issues.updates(id) });
    }
  };
}

export function useCreateIssue() {
  const invalidate = useInvalidateIssue();
  return useMutation({
    mutationFn: (body: IssueCreate) => createIssue(body),
    onSuccess: invalidate,
  });
}

export function useUpdateIssue(id: string) {
  const invalidate = useInvalidateIssue(id);
  return useMutation({
    mutationFn: (body: IssueMetadataUpdate) => updateIssue(id, body),
    onSuccess: invalidate,
  });
}

export function useChangeStatus(id: string) {
  const invalidate = useInvalidateIssue(id);
  return useMutation({
    mutationFn: (body: IssueStatusChangeRequest) => changeStatus(id, body),
    onSuccess: invalidate,
  });
}

export function useCloseIssue(id: string) {
  const invalidate = useInvalidateIssue(id);
  return useMutation({
    mutationFn: (body: IssueCloseRequest) => closeIssue(id, body),
    onSuccess: invalidate,
  });
}

export function useReopenIssue(id: string) {
  const invalidate = useInvalidateIssue(id);
  return useMutation({
    mutationFn: (body: IssueReopenRequest) => reopenIssue(id, body),
    onSuccess: invalidate,
  });
}

export function useAddFollowUp(id: string) {
  const invalidate = useInvalidateIssue(id);
  return useMutation({
    mutationFn: (body: IssueUpdateCreate) => addFollowUp(id, body),
    onSuccess: invalidate,
  });
}

export function useVoidUpdate(issueId: string) {
  // Voiding changes the issue's derived state, timeline, dashboard, and lists —
  // the standard issue invalidation covers all of them.
  const invalidate = useInvalidateIssue(issueId);
  return useMutation({
    mutationFn: ({ updateId, body }: { updateId: string; body: IssueUpdateVoidRequest }) =>
      voidUpdate(issueId, updateId, body),
    onSuccess: invalidate,
  });
}
