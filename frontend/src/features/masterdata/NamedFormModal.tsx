// Concept by MrHan (08974747477)
import { type FormEvent, useState } from 'react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { Field, TextInput, TextArea } from '@/components/ui/Field';
import { InlineError } from '@/components/feedback/InlineError';
import { useToast } from '@/components/feedback/ToastProvider';
import { useCreateNamed, useUpdateNamed, type NamedResourceKind } from '@/api/masterdataAdmin';
import type { NamedCreate, NamedResponse, NamedUpdate } from '@/api/types';

const NAME_MAX = 150;

/**
 * Create or edit a named master-data record. Sends ONLY `name`/`description`
 * (the sole fields the NamedCreate/NamedUpdate schemas permit); edit is
 * diff-based. Validation/conflict errors render inline next to the form.
 */
export function NamedFormModal({
  kind,
  singular,
  existing,
  onClose,
}: {
  kind: NamedResourceKind;
  singular: string;
  existing?: NamedResponse;
  onClose: () => void;
}) {
  const isEdit = !!existing;
  const toast = useToast();
  const [name, setName] = useState(existing?.name ?? '');
  const [description, setDescription] = useState(existing?.description ?? '');

  const create = useCreateNamed(kind);
  const update = useUpdateNamed(kind);
  const pending = create.isPending || update.isPending;
  const error = create.error ?? update.error;

  function submit(e: FormEvent) {
    e.preventDefault();
    const trimmedName = name.trim();
    if (!trimmedName) return;
    const desc = description.trim() ? description.trim() : null;

    if (isEdit) {
      const body: NamedUpdate = {};
      if (trimmedName !== existing!.name) body.name = trimmedName;
      if (desc !== (existing!.description ?? null)) body.description = desc;
      if (Object.keys(body).length === 0) {
        onClose(); // nothing changed
        return;
      }
      update.mutate(
        { id: existing!.id, body },
        {
          onSuccess: () => {
            toast.success(`${singular} updated.`);
            onClose();
          },
        },
      );
    } else {
      const body: NamedCreate = { name: trimmedName, description: desc };
      create.mutate(body, {
        onSuccess: () => {
          toast.success(`${singular} created.`);
          onClose();
        },
      });
    }
  }

  return (
    <Modal title={isEdit ? `Edit ${singular.toLowerCase()}` : `New ${singular.toLowerCase()}`} onClose={onClose}>
      <form onSubmit={submit} className="space-y-3">
        <Field label="Name" htmlFor="named-name" required>
          <TextInput
            id="named-name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            maxLength={NAME_MAX}
            required
            autoFocus
          />
        </Field>
        <Field label="Description" htmlFor="named-desc">
          <TextArea
            id="named-desc"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Optional"
          />
        </Field>
        {error != null && <InlineError error={error} />}
        <div className="flex justify-end gap-2 pt-1">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" loading={pending} disabled={!name.trim()}>
            {isEdit ? 'Save changes' : `Create ${singular.toLowerCase()}`}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
