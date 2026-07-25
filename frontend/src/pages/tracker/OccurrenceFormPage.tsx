// Concept by MrHan (08974747477)
import { type FormEvent, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { usePageTitle } from '@/hooks/usePageTitle';
import { PageHeader } from '@/components/layout/PageHeader';
import { DataState } from '@/components/feedback/DataState';
import { InlineError } from '@/components/feedback/InlineError';
import { Button } from '@/components/ui/Button';
import { Field, Select, TextArea, TextInput } from '@/components/ui/Field';
import { useToast } from '@/components/feedback/ToastProvider';
import { useMeetingTypes } from '@/api/masterdata';
import { useCreateOccurrence, useOccurrence, useUpdateOccurrence } from '@/api/meetings';
import type {
  MeetingOccurrence,
  MeetingOccurrenceCreate,
  MeetingOccurrenceUpdate,
} from '@/api/types';

interface OccForm {
  meeting_date: string;
  meeting_number: string;
  reference_number: string;
  agenda: string;
  minutes_link: string;
  notes: string;
}

const EMPTY: OccForm = {
  meeting_date: '',
  meeting_number: '',
  reference_number: '',
  agenda: '',
  minutes_link: '',
  notes: '',
};

/** Empty string -> null (optional contract fields are `string | null`). */
const orNull = (value: string): string | null => (value.trim() ? value.trim() : null);

/** Shared optional fields for both create and edit. `meeting_date` is date-only
 *  and sent verbatim (the native date input value is already `YYYY-MM-DD`, so no
 *  Date object is constructed and no timezone shift can occur). */
function OccurrenceFields({
  form,
  set,
}: {
  form: OccForm;
  set: (key: keyof OccForm, value: string) => void;
}) {
  return (
    <>
      <Field label="Meeting date" htmlFor="occ-date" required>
        <TextInput
          id="occ-date"
          type="date"
          value={form.meeting_date}
          onChange={(e) => set('meeting_date', e.target.value)}
          required
        />
      </Field>
      <Field label="Meeting number" htmlFor="occ-number">
        <TextInput
          id="occ-number"
          maxLength={50}
          value={form.meeting_number}
          onChange={(e) => set('meeting_number', e.target.value)}
        />
      </Field>
      <Field label="Reference number" htmlFor="occ-ref">
        <TextInput
          id="occ-ref"
          maxLength={100}
          value={form.reference_number}
          onChange={(e) => set('reference_number', e.target.value)}
        />
      </Field>
      <Field label="Agenda" htmlFor="occ-agenda">
        <TextArea
          id="occ-agenda"
          value={form.agenda}
          onChange={(e) => set('agenda', e.target.value)}
        />
      </Field>
      <Field label="Minutes link" htmlFor="occ-minutes">
        <TextInput
          id="occ-minutes"
          type="url"
          placeholder="https://…"
          value={form.minutes_link}
          onChange={(e) => set('minutes_link', e.target.value)}
        />
      </Field>
      <Field label="Notes" htmlFor="occ-notes">
        <TextArea id="occ-notes" value={form.notes} onChange={(e) => set('notes', e.target.value)} />
      </Field>
    </>
  );
}

export function OccurrenceFormPage() {
  const { meetingId } = useParams();
  return meetingId ? <EditOccurrence id={meetingId} /> : <CreateOccurrence />;
}

function CreateOccurrence() {
  usePageTitle('New meeting occurrence');
  const navigate = useNavigate();
  const toast = useToast();
  const types = useMeetingTypes();
  const create = useCreateOccurrence();
  const [meetingType, setMeetingType] = useState('');
  const [form, setForm] = useState<OccForm>(EMPTY);
  const set = (key: keyof OccForm, value: string) => setForm((f) => ({ ...f, [key]: value }));

  const canSubmit = !!meetingType && !!form.meeting_date;

  function submit(e: FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;
    const body: MeetingOccurrenceCreate = {
      meeting_id: meetingType,
      meeting_date: form.meeting_date,
      meeting_number: orNull(form.meeting_number),
      reference_number: orNull(form.reference_number),
      agenda: orNull(form.agenda),
      minutes_link: orNull(form.minutes_link),
      notes: orNull(form.notes),
    };
    create.mutate(body, {
      onSuccess: (occ) => {
        toast.success('Meeting occurrence created.');
        navigate(`/app/meetings/${occ.id}`);
      },
    });
  }

  return (
    <section>
      <PageHeader
        title="New meeting occurrence"
        backTo="/app/meetings"
        backLabel="Back to meetings"
      />
      <form
        onSubmit={submit}
        className="max-w-xl space-y-3 rounded-lg border border-border bg-surface p-4"
      >
        <Field label="Meeting type" htmlFor="occ-type" required>
          <Select
            id="occ-type"
            value={meetingType}
            onChange={(e) => setMeetingType(e.target.value)}
            required
          >
            <option value="">Select a meeting type…</option>
            {types.data?.items.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </Select>
        </Field>
        <OccurrenceFields form={form} set={set} />
        {create.error != null && <InlineError error={create.error} />}
        <div className="flex justify-end gap-2">
          <Button type="button" variant="ghost" onClick={() => navigate('/app/meetings')}>
            Cancel
          </Button>
          <Button type="submit" loading={create.isPending} disabled={!canSubmit}>
            Create occurrence
          </Button>
        </div>
      </form>
    </section>
  );
}

function EditOccurrence({ id }: { id: string }) {
  usePageTitle('Edit meeting occurrence');
  const occ = useOccurrence(id);
  const types = useMeetingTypes();
  const typeName = occ.data
    ? types.data?.items.find((t) => t.id === occ.data!.meeting_id)?.name
    : undefined;

  return (
    <section>
      <PageHeader
        title="Edit meeting occurrence"
        backTo={`/app/meetings/${id}`}
        backLabel="Back to meeting"
      />
      <DataState isLoading={occ.isLoading} error={occ.error} loadingLabel="Loading meeting…">
        {occ.data && <EditForm occurrence={occ.data} typeName={typeName} />}
      </DataState>
    </section>
  );
}

function EditForm({
  occurrence,
  typeName,
}: {
  occurrence: MeetingOccurrence;
  typeName: string | undefined;
}) {
  const navigate = useNavigate();
  const toast = useToast();
  const update = useUpdateOccurrence(occurrence.id);
  const [form, setForm] = useState<OccForm>({
    meeting_date: occurrence.meeting_date,
    meeting_number: occurrence.meeting_number ?? '',
    reference_number: occurrence.reference_number ?? '',
    agenda: occurrence.agenda ?? '',
    minutes_link: occurrence.minutes_link ?? '',
    notes: occurrence.notes ?? '',
  });
  const set = (key: keyof OccForm, value: string) => setForm((f) => ({ ...f, [key]: value }));

  function submit(e: FormEvent) {
    e.preventDefault();
    if (!form.meeting_date) return;
    // Diff against the loaded occurrence — send only changed fields. The meeting
    // TYPE is immutable (not present in MeetingOccurrenceUpdate), so it is shown
    // read-only and never sent.
    const body: MeetingOccurrenceUpdate = {};
    if (form.meeting_date !== occurrence.meeting_date) body.meeting_date = form.meeting_date;
    if (orNull(form.meeting_number) !== (occurrence.meeting_number ?? null))
      body.meeting_number = orNull(form.meeting_number);
    if (orNull(form.reference_number) !== (occurrence.reference_number ?? null))
      body.reference_number = orNull(form.reference_number);
    if (orNull(form.agenda) !== (occurrence.agenda ?? null)) body.agenda = orNull(form.agenda);
    if (orNull(form.minutes_link) !== (occurrence.minutes_link ?? null))
      body.minutes_link = orNull(form.minutes_link);
    if (orNull(form.notes) !== (occurrence.notes ?? null)) body.notes = orNull(form.notes);

    if (Object.keys(body).length === 0) {
      navigate(`/app/meetings/${occurrence.id}`);
      return;
    }
    update.mutate(body, {
      onSuccess: () => {
        toast.success('Meeting occurrence updated.');
        navigate(`/app/meetings/${occurrence.id}`);
      },
    });
  }

  return (
    <form
      onSubmit={submit}
      className="max-w-xl space-y-3 rounded-lg border border-border bg-surface p-4"
    >
      <Field label="Meeting type" htmlFor="occ-type-ro" hint="The meeting type cannot be changed.">
        <TextInput id="occ-type-ro" value={typeName ?? 'Meeting'} readOnly disabled />
      </Field>
      <OccurrenceFields form={form} set={set} />
      {update.error != null && <InlineError error={update.error} />}
      <div className="flex justify-end gap-2">
        <Button
          type="button"
          variant="ghost"
          onClick={() => navigate(`/app/meetings/${occurrence.id}`)}
        >
          Cancel
        </Button>
        <Button type="submit" loading={update.isPending} disabled={!form.meeting_date}>
          Save changes
        </Button>
      </div>
    </form>
  );
}
