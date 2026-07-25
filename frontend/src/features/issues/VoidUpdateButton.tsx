// Concept by MrHan (08974747477)
import { type FormEvent, useState } from 'react';
import { useVoidUpdate } from '@/api/issues';
import type { IssueUpdateResponse } from '@/api/types';
import { useToast } from '@/components/feedback/ToastProvider';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { Field, TextArea } from '@/components/ui/Field';
import { InlineError } from '@/components/feedback/InlineError';

/** ADMIN-only action to void a follow-up update. Voiding is permanent (the
 *  history table is append-only). Used inside the issue Timeline. */
export function VoidUpdateButton({
  issueId,
  update,
}: {
  issueId: string;
  update: IssueUpdateResponse;
}) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <Button type="button" variant="ghost" onClick={() => setOpen(true)}>
        Void
      </Button>
      {open && (
        <VoidModal issueId={issueId} update={update} onClose={() => setOpen(false)} />
      )}
    </>
  );
}

function VoidModal({
  issueId,
  update,
  onClose,
}: {
  issueId: string;
  update: IssueUpdateResponse;
  onClose: () => void;
}) {
  const toast = useToast();
  const voidMutation = useVoidUpdate(issueId);
  // Kept in state so a recoverable API error never loses the typed reason.
  const [reason, setReason] = useState('');

  function submit(e: FormEvent) {
    e.preventDefault();
    if (!reason.trim()) return;
    voidMutation.mutate(
      { updateId: update.id, body: { void_reason: reason.trim() } },
      {
        onSuccess: () => {
          toast.success('Follow-up update voided.');
          onClose();
        },
        // On error the modal stays open and `reason` is preserved; the error is
        // shown inline below.
      },
    );
  }

  return (
    <Modal title="Void follow-up update" onClose={onClose}>
      <form onSubmit={submit} className="space-y-3">
        <div
          role="alert"
          className="rounded-md border border-amber-300 bg-amber-50 p-2 text-xs text-amber-800"
        >
          This <span className="font-semibold">permanently voids</span> the follow-up update and
          cannot be undone.
        </div>
        <Field label="Reason" htmlFor="void-reason" required>
          <TextArea
            id="void-reason"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            maxLength={500}
            required
            autoFocus
          />
        </Field>
        {voidMutation.error != null && <InlineError error={voidMutation.error} />}
        <div className="flex justify-end gap-2">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" loading={voidMutation.isPending} disabled={!reason.trim()}>
            Void update
          </Button>
        </div>
      </form>
    </Modal>
  );
}
