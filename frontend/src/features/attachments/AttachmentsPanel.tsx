// Concept by MrHan (08974747477)
import { type FormEvent, useRef, useState } from 'react';
import { Download, Paperclip, Trash2, Upload } from 'lucide-react';
import { ApiError } from '@/api/errors';
import {
  useAttachments,
  useDownloadAttachment,
  useRemoveAttachment,
  useUploadAttachment,
} from '@/api/attachments';
import type { AttachmentResponse } from '@/api/types';
import { useAuth } from '@/auth/useAuth';
import { useToast } from '@/components/feedback/ToastProvider';
import { Button } from '@/components/ui/Button';
import { Field, TextInput } from '@/components/ui/Field';
import { Modal } from '@/components/ui/Modal';
import { DataState } from '@/components/feedback/DataState';
import { InlineError } from '@/components/feedback/InlineError';
import { formatDateTime } from '@/lib/dates';
import {
  ATTACHMENT_ACCEPT,
  ATTACHMENT_MAX_MB,
  formatBytes,
  precheckAttachment,
} from './config';

/**
 * Map an upload failure to a specific, plain-text message. The three attachment
 * rejection codes (413 too-large, 415 type-not-allowed, 415 content-mismatch)
 * are handled distinctly.
 */
function uploadErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.code) {
      case 'ATTACHMENT_TOO_LARGE':
        return `File exceeds the maximum size (${ATTACHMENT_MAX_MB} MB).`;
      case 'ATTACHMENT_TYPE_NOT_ALLOWED':
        return 'That file type is not allowed. Upload a PDF, JPEG, or PNG.';
      case 'ATTACHMENT_CONTENT_MISMATCH':
        return 'The file content does not match its type. Upload a genuine PDF, JPEG, or PNG.';
      case 'ISSUE_ARCHIVED':
        return 'This issue is archived and cannot receive attachments.';
      default:
        return error.message;
    }
  }
  return 'Upload failed. Please try again.';
}

export function AttachmentsPanel({ issueId, archived }: { issueId: string; archived: boolean }) {
  const { hasRole } = useAuth();
  const toast = useToast();
  const list = useAttachments(issueId);

  const canUpload = hasRole('EDITOR', 'ADMIN') && !archived;
  const canRemove = hasRole('ADMIN');

  return (
    <section className="mt-6">
      <h2 className="mb-2 flex items-center gap-2 text-sm font-semibold text-text">
        <Paperclip className="h-4 w-4" aria-hidden="true" /> Attachments
      </h2>

      {canUpload && <UploadForm issueId={issueId} />}

      <DataState
        isLoading={list.isLoading}
        error={list.error}
        isEmpty={(list.data?.length ?? 0) === 0}
        loadingLabel="Loading attachments…"
        emptyTitle="No attachments yet"
        emptyDescription={canUpload ? 'Upload a PDF, JPEG, or PNG above.' : undefined}
      >
        <ul className="space-y-2">
          {list.data?.map((att) => (
            <AttachmentItem
              key={att.id}
              issueId={issueId}
              attachment={att}
              canRemove={canRemove}
              onRemoved={() => toast.success('Attachment removed.')}
            />
          ))}
        </ul>
      </DataState>
    </section>
  );
}

function UploadForm({ issueId }: { issueId: string }) {
  const toast = useToast();
  const upload = useUploadAttachment(issueId);
  const fileRef = useRef<HTMLInputElement>(null);
  const [description, setDescription] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLocalError(null);
    const file = fileRef.current?.files?.[0];
    if (!file) {
      setLocalError('Choose a file to upload.');
      return;
    }
    // Usability pre-check (the backend re-validates and is authoritative).
    const check = precheckAttachment(file);
    if (!check.ok) {
      setLocalError(check.reason);
      toast.error(check.reason);
      return;
    }
    upload.mutate(
      { file, description },
      {
        onSuccess: () => {
          toast.success('Attachment uploaded.');
          setDescription('');
          fileRef.current?.form?.reset();
        },
        onError: (err) => {
          const msg = uploadErrorMessage(err);
          setLocalError(msg);
          toast.error(msg);
        },
      },
    );
  }

  return (
    <form
      onSubmit={onSubmit}
      className="mb-4 space-y-3 rounded-lg border border-border bg-surface p-3"
      aria-label="Upload attachment"
    >
      <Field label="File" htmlFor="att-file" hint={`PDF, JPEG, or PNG · up to ${ATTACHMENT_MAX_MB} MB`}>
        <input
          ref={fileRef}
          id="att-file"
          name="file"
          type="file"
          accept={ATTACHMENT_ACCEPT}
          className="mt-1 block w-full text-sm text-text file:mr-3 file:rounded-md file:border-0 file:bg-primary file:px-3 file:py-2 file:text-sm file:font-medium file:text-primary-fg"
          onChange={() => setLocalError(null)}
        />
      </Field>
      <Field label="Description" htmlFor="att-desc">
        <TextInput
          id="att-desc"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Optional note about this file"
          maxLength={500}
        />
      </Field>
      {localError && <InlineError error={new Error(localError)} />}
      <div className="flex justify-end">
        <Button type="submit" loading={upload.isPending}>
          <Upload className="h-4 w-4" aria-hidden="true" /> Upload
        </Button>
      </div>
    </form>
  );
}

function AttachmentItem({
  issueId,
  attachment,
  canRemove,
  onRemoved,
}: {
  issueId: string;
  attachment: AttachmentResponse;
  canRemove: boolean;
  onRemoved: () => void;
}) {
  const toast = useToast();
  const download = useDownloadAttachment(issueId);
  const remove = useRemoveAttachment(issueId);
  const [confirming, setConfirming] = useState(false);

  function onDownload() {
    download.mutate(attachment, {
      onError: () => toast.error('Download failed. Please try again.'),
    });
  }

  function onConfirmRemove() {
    remove.mutate(attachment.id, {
      onSuccess: () => {
        setConfirming(false);
        onRemoved();
      },
      onError: (err) =>
        toast.error(err instanceof ApiError ? err.message : 'Could not remove the attachment.'),
    });
  }

  return (
    <li className="flex flex-wrap items-center gap-3 rounded-md border border-border bg-surface p-3">
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-text">{attachment.original_filename}</p>
        <p className="text-xs text-muted">
          {attachment.mime_type} · {formatBytes(attachment.size_bytes)} ·{' '}
          {formatDateTime(attachment.uploaded_at)}
          {attachment.checksum_sha256 && (
            <>
              {' '}
              · <span className="font-mono">sha256:{attachment.checksum_sha256.slice(0, 8)}</span>
            </>
          )}
        </p>
        {attachment.description && (
          <p className="mt-0.5 text-xs text-text">{attachment.description}</p>
        )}
      </div>
      <div className="flex items-center gap-2">
        <Button
          type="button"
          variant="secondary"
          loading={download.isPending}
          onClick={onDownload}
        >
          <Download className="h-4 w-4" aria-hidden="true" /> Download
        </Button>
        {canRemove && (
          <Button
            type="button"
            variant="ghost"
            onClick={() => setConfirming(true)}
            aria-label={`Remove ${attachment.original_filename}`}
          >
            <Trash2 className="h-4 w-4 text-danger" aria-hidden="true" />
          </Button>
        )}
      </div>

      {confirming && (
        <Modal title="Remove attachment" onClose={() => setConfirming(false)}>
          <p className="text-sm text-text">
            Remove <span className="font-medium">{attachment.original_filename}</span>? This hides it
            from the issue.
          </p>
          <div className="mt-4 flex justify-end gap-2">
            <Button type="button" variant="ghost" onClick={() => setConfirming(false)}>
              Cancel
            </Button>
            <Button type="button" loading={remove.isPending} onClick={onConfirmRemove}>
              Remove
            </Button>
          </div>
        </Modal>
      )}
    </li>
  );
}
