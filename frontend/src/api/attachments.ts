// Concept by MrHan (08974747477)
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';
import { queryKeys } from './queryKeys';
import { sanitizeFilename, triggerBrowserDownload } from '@/lib/download';
import type { AttachmentResponse } from './types';

export interface UploadAttachmentInput {
  file: File;
  description?: string;
}

// ---- fetchers ----
export function listAttachments(issueId: string): Promise<AttachmentResponse[]> {
  return apiClient.get<AttachmentResponse[]>(`/issues/${issueId}/attachments`);
}

export function uploadAttachment(
  issueId: string,
  { file, description }: UploadAttachmentInput,
): Promise<AttachmentResponse> {
  const form = new FormData();
  form.append('file', file);
  if (description && description.trim()) form.append('description', description.trim());
  return apiClient.post<AttachmentResponse>(`/issues/${issueId}/attachments`, { formData: form });
}

export function removeAttachment(issueId: string, attachmentId: string): Promise<{ message: string }> {
  return apiClient.post<{ message: string }>(
    `/issues/${issueId}/attachments/${attachmentId}/remove`,
  );
}

/**
 * Download an attachment to the user's device. The blob and its object URL are
 * created and revoked entirely within this call — nothing is cached. The stored
 * filename comes from Content-Disposition, falling back to the (sanitized)
 * original filename we already hold.
 */
export async function downloadAttachment(
  issueId: string,
  attachment: Pick<AttachmentResponse, 'id' | 'original_filename'>,
): Promise<void> {
  const { blob, filename } = await apiClient.download(
    `/issues/${issueId}/attachments/${attachment.id}/download`,
  );
  const fallback = sanitizeFilename(attachment.original_filename) || 'attachment';
  triggerBrowserDownload(blob, filename ?? fallback);
}

// ---- hooks ----
export function useAttachments(issueId: string) {
  return useQuery({
    queryKey: queryKeys.issues.attachments(issueId),
    queryFn: () => listAttachments(issueId),
    enabled: !!issueId,
  });
}

function useInvalidateAttachments(issueId: string) {
  const qc = useQueryClient();
  return () => {
    qc.invalidateQueries({ queryKey: queryKeys.issues.attachments(issueId) });
    qc.invalidateQueries({ queryKey: queryKeys.issues.detail(issueId) });
  };
}

export function useUploadAttachment(issueId: string) {
  const invalidate = useInvalidateAttachments(issueId);
  return useMutation({
    mutationFn: (input: UploadAttachmentInput) => uploadAttachment(issueId, input),
    onSuccess: invalidate,
  });
}

export function useRemoveAttachment(issueId: string) {
  const invalidate = useInvalidateAttachments(issueId);
  return useMutation({
    mutationFn: (attachmentId: string) => removeAttachment(issueId, attachmentId),
    onSuccess: invalidate,
  });
}

/** Imperative download mutation (blob never enters the query cache). */
export function useDownloadAttachment(issueId: string) {
  return useMutation({
    mutationFn: (attachment: Pick<AttachmentResponse, 'id' | 'original_filename'>) =>
      downloadAttachment(issueId, attachment),
  });
}
