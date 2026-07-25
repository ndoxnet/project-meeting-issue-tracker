// Concept by MrHan (08974747477)
import { type FormEvent, useState } from 'react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { Field, TextInput } from '@/components/ui/Field';
import { InlineError } from '@/components/feedback/InlineError';
import { useToast } from '@/components/feedback/ToastProvider';
import { useResetUserPassword } from '@/api/users';
import type { UserResponse } from '@/api/types';

const PASSWORD_MIN = 12;

export function ResetPasswordModal({
  user,
  onClose,
}: {
  user: UserResponse;
  onClose: () => void;
}) {
  const toast = useToast();
  const reset = useResetUserPassword(user.id);
  const [password, setPassword] = useState('');

  function submit(e: FormEvent) {
    e.preventDefault();
    if (password.length < PASSWORD_MIN) return;
    reset.mutate(
      { new_password: password },
      {
        onSuccess: () => {
          toast.success(`Password reset for ${user.username}.`);
          onClose();
        },
        // On error the modal stays open and the typed value is preserved.
      },
    );
  }

  return (
    <Modal title={`Reset password — ${user.username}`} onClose={onClose}>
      <form onSubmit={submit} className="space-y-3">
        <div
          role="note"
          className="rounded-md border border-amber-300 bg-amber-50 p-2 text-xs text-amber-800"
        >
          The user&rsquo;s existing signed-in sessions remain valid until their tokens expire —
          backend token revocation is planned as a production hardening task. To block access
          immediately, deactivate the user instead.
        </div>
        <Field
          label="New password"
          htmlFor="reset-password"
          required
          hint={`At least ${PASSWORD_MIN} characters; must not equal the username or email.`}
        >
          <TextInput
            id="reset-password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            minLength={PASSWORD_MIN}
            maxLength={128}
            autoComplete="new-password"
            required
            autoFocus
          />
        </Field>
        {reset.error != null && <InlineError error={reset.error} />}
        <div className="flex justify-end gap-2 pt-1">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" loading={reset.isPending} disabled={password.length < PASSWORD_MIN}>
            Reset password
          </Button>
        </div>
      </form>
    </Modal>
  );
}
