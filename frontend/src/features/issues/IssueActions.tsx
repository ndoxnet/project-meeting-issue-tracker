// Concept by MrHan (08974747477)
import { useState } from 'react';
import type { IssueDetailResponse, IssueStatus } from '@/api/types';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { Field, Select, TextArea, TextInput } from '@/components/ui/Field';
import { InlineError } from '@/components/feedback/InlineError';
import {
  useAddFollowUp,
  useChangeStatus,
  useCloseIssue,
  useReopenIssue,
} from '@/api/issues';
import { allowedStatusTargets, canClose, canReopen } from './lifecycle';

const today = () => new Date().toISOString().slice(0, 10);
type Which = 'status' | 'close' | 'reopen' | 'followup' | null;

/** Lifecycle actions on the issue detail page (Editor/Admin only, non-archived). */
export function IssueActions({ issue }: { issue: IssueDetailResponse }) {
  const [open, setOpen] = useState<Which>(null);
  const close = () => setOpen(null);

  const statusTargets = allowedStatusTargets(issue.status);

  return (
    <div className="flex flex-wrap gap-2">
      {statusTargets.length > 0 && (
        <Button variant="secondary" onClick={() => setOpen('status')}>
          Change status
        </Button>
      )}
      {canClose(issue.status) && (
        <Button variant="secondary" onClick={() => setOpen('close')}>
          Close
        </Button>
      )}
      {canReopen(issue.status) && (
        <Button variant="secondary" onClick={() => setOpen('reopen')}>
          Reopen
        </Button>
      )}
      <Button variant="secondary" onClick={() => setOpen('followup')}>
        Add follow-up
      </Button>

      {open === 'status' && (
        <ChangeStatusModal issueId={issue.id} targets={statusTargets} onDone={close} />
      )}
      {open === 'close' && (
        <CloseModal issueId={issue.id} raisedDate={issue.raised_date} onDone={close} />
      )}
      {open === 'reopen' && <ReopenModal issueId={issue.id} onDone={close} />}
      {open === 'followup' && <FollowUpModal issueId={issue.id} onDone={close} />}
    </div>
  );
}

function ChangeStatusModal({
  issueId,
  targets,
  onDone,
}: {
  issueId: string;
  targets: IssueStatus[];
  onDone: () => void;
}) {
  const [newStatus, setNewStatus] = useState<IssueStatus>(targets[0]);
  const [note, setNote] = useState('');
  const m = useChangeStatus(issueId);
  return (
    <Modal title="Change status" onClose={onDone}>
      <form
        className="space-y-3"
        onSubmit={(e) => {
          e.preventDefault();
          m.mutate({ new_status: newStatus, note }, { onSuccess: onDone });
        }}
      >
        <Field label="New status" htmlFor="cs-status" required>
          <Select
            id="cs-status"
            value={newStatus}
            onChange={(e) => setNewStatus(e.target.value as IssueStatus)}
          >
            {targets.map((t) => (
              <option key={t} value={t}>
                {t.replace('_', ' ')}
              </option>
            ))}
          </Select>
        </Field>
        <Field label="Note" htmlFor="cs-note" required>
          <TextArea id="cs-note" value={note} onChange={(e) => setNote(e.target.value)} required />
        </Field>
        {m.error != null && <InlineError error={m.error} />}
        <ModalActions onCancel={onDone} pending={m.isPending} submitLabel="Update status" disabled={!note.trim()} />
      </form>
    </Modal>
  );
}

function CloseModal({
  issueId,
  raisedDate,
  onDone,
}: {
  issueId: string;
  raisedDate: string;
  onDone: () => void;
}) {
  const [note, setNote] = useState('');
  const [date, setDate] = useState(today());
  const m = useCloseIssue(issueId);
  return (
    <Modal title="Close issue" onClose={onDone}>
      <form
        className="space-y-3"
        onSubmit={(e) => {
          e.preventDefault();
          m.mutate({ closure_note: note, closed_date: date }, { onSuccess: onDone });
        }}
      >
        <Field label="Closure note" htmlFor="close-note" required>
          <TextArea id="close-note" value={note} onChange={(e) => setNote(e.target.value)} required />
        </Field>
        <Field label="Closed date" htmlFor="close-date" required hint={`Not before raised date (${raisedDate})`}>
          <TextInput
            id="close-date"
            type="date"
            min={raisedDate}
            value={date}
            onChange={(e) => setDate(e.target.value)}
            required
          />
        </Field>
        {m.error != null && <InlineError error={m.error} />}
        <ModalActions onCancel={onDone} pending={m.isPending} submitLabel="Close issue" disabled={!note.trim()} />
      </form>
    </Modal>
  );
}

function ReopenModal({ issueId, onDone }: { issueId: string; onDone: () => void }) {
  const [reason, setReason] = useState('');
  const [date, setDate] = useState(today());
  const m = useReopenIssue(issueId);
  return (
    <Modal title="Reopen issue" onClose={onDone}>
      <form
        className="space-y-3"
        onSubmit={(e) => {
          e.preventDefault();
          m.mutate({ reason, reopen_date: date }, { onSuccess: onDone });
        }}
      >
        <Field label="Reason" htmlFor="reopen-reason" required>
          <TextArea
            id="reopen-reason"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            required
          />
        </Field>
        <Field label="Reopen date" htmlFor="reopen-date" required>
          <TextInput
            id="reopen-date"
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            required
          />
        </Field>
        {m.error != null && <InlineError error={m.error} />}
        <ModalActions onCancel={onDone} pending={m.isPending} submitLabel="Reopen issue" disabled={!reason.trim()} />
      </form>
    </Modal>
  );
}

function FollowUpModal({ issueId, onDone }: { issueId: string; onDone: () => void }) {
  const [note, setNote] = useState('');
  const [date, setDate] = useState(today());
  const [nextAction, setNextAction] = useState('');
  const m = useAddFollowUp(issueId);
  return (
    <Modal title="Add follow-up" onClose={onDone}>
      <form
        className="space-y-3"
        onSubmit={(e) => {
          e.preventDefault();
          m.mutate(
            { update_date: date, update_note: note, next_action: nextAction || null },
            { onSuccess: onDone },
          );
        }}
      >
        <Field label="Update date" htmlFor="fu-date" required>
          <TextInput
            id="fu-date"
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            required
          />
        </Field>
        <Field label="Update note" htmlFor="fu-note" required>
          <TextArea id="fu-note" value={note} onChange={(e) => setNote(e.target.value)} required />
        </Field>
        <Field label="Next action" htmlFor="fu-next">
          <TextInput
            id="fu-next"
            value={nextAction}
            onChange={(e) => setNextAction(e.target.value)}
          />
        </Field>
        {m.error != null && <InlineError error={m.error} />}
        <ModalActions onCancel={onDone} pending={m.isPending} submitLabel="Add follow-up" disabled={!note.trim()} />
      </form>
    </Modal>
  );
}

function ModalActions({
  onCancel,
  pending,
  submitLabel,
  disabled,
}: {
  onCancel: () => void;
  pending: boolean;
  submitLabel: string;
  disabled?: boolean;
}) {
  return (
    <div className="flex justify-end gap-2 pt-1">
      <Button type="button" variant="ghost" onClick={onCancel}>
        Cancel
      </Button>
      <Button type="submit" loading={pending} disabled={disabled}>
        {submitLabel}
      </Button>
    </div>
  );
}
