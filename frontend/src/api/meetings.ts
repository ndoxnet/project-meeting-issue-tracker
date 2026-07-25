// Concept by MrHan (08974747477)
// "Meetings" in the UI are backed by meeting OCCURRENCES (dated instances that
// relate to issues). Meeting TYPES (master data) provide the type name.
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';
import { queryKeys } from './queryKeys';
import type {
  MeetingOccurrence,
  MeetingOccurrenceCreate,
  MeetingOccurrenceUpdate,
  Page,
} from './types';

export interface MeetingOccurrenceFilters {
  page?: number;
  page_size?: number;
  meeting_id?: string;
}

export function listOccurrences(
  filters: MeetingOccurrenceFilters,
): Promise<Page<MeetingOccurrence>> {
  return apiClient.get<Page<MeetingOccurrence>>('/meeting-occurrences', {
    query: {
      page: filters.page ?? 1,
      page_size: filters.page_size ?? 20,
      meeting_id: filters.meeting_id,
    },
  });
}

export function getOccurrence(id: string): Promise<MeetingOccurrence> {
  return apiClient.get<MeetingOccurrence>(`/meeting-occurrences/${id}`);
}

export function createOccurrence(body: MeetingOccurrenceCreate): Promise<MeetingOccurrence> {
  return apiClient.post<MeetingOccurrence>('/meeting-occurrences', { json: body });
}

export function updateOccurrence(
  id: string,
  body: MeetingOccurrenceUpdate,
): Promise<MeetingOccurrence> {
  return apiClient.patch<MeetingOccurrence>(`/meeting-occurrences/${id}`, { json: body });
}

export function useOccurrences(filters: MeetingOccurrenceFilters) {
  return useQuery({
    queryKey: queryKeys.meetings.occurrences(filters),
    queryFn: () => listOccurrences(filters),
  });
}

export function useOccurrence(id: string) {
  return useQuery({
    queryKey: queryKeys.meetings.occurrence(id),
    queryFn: () => getOccurrence(id),
    enabled: !!id,
  });
}

/** Invalidate occurrence lists, an optional detail, and dashboard (recent meetings). */
function useInvalidateOccurrences() {
  const qc = useQueryClient();
  return (id?: string) => {
    qc.invalidateQueries({ queryKey: ['meeting-occurrences'] });
    qc.invalidateQueries({ queryKey: ['dashboard'] });
    if (id) qc.invalidateQueries({ queryKey: queryKeys.meetings.occurrence(id) });
  };
}

export function useCreateOccurrence() {
  const invalidate = useInvalidateOccurrences();
  return useMutation({
    mutationFn: (body: MeetingOccurrenceCreate) => createOccurrence(body),
    onSuccess: () => invalidate(),
  });
}

export function useUpdateOccurrence(id: string) {
  const invalidate = useInvalidateOccurrences();
  return useMutation({
    mutationFn: (body: MeetingOccurrenceUpdate) => updateOccurrence(id, body),
    onSuccess: () => invalidate(id),
  });
}
