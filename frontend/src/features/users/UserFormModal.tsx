// Concept by MrHan (08974747477)
import { type FormEvent, useState } from 'react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { Field, Select, TextInput } from '@/components/ui/Field';
import { InlineError } from '@/components/feedback/InlineError';
import { useToast } from '@/components/feedback/ToastProvider';
import { useCreateUser, useUpdateUser } from '@/api/users';
import { USER_ROLES, type UserCreate, type UserResponse, type UserRole, type UserUpdate } from '@/api/types';

const PASSWORD_MIN = 12; // mirrors the backend policy (backend is authoritative)

export function UserFormModal({
  existing,
  isSelf = false,
  onClose,
}: {
  existing?: UserResponse;
  isSelf?: boolean;
  onClose: () => void;
}) {
  const isEdit = !!existing;
  const toast = useToast();

  const [username, setUsername] = useState(existing?.username ?? '');
  const [email, setEmail] = useState(existing?.email ?? '');
  const [fullName, setFullName] = useState(existing?.full_name ?? '');
  const [role, setRole] = useState<UserRole>(existing?.role ?? 'VIEWER');
  const [password, setPassword] = useState('');

  const create = useCreateUser();
  const update = useUpdateUser(existing?.id ?? '');
  const pending = create.isPending || update.isPending;
  const error = create.error ?? update.error;

  const createValid =
    username.trim().length >= 3 &&
    !!email.trim() &&
    !!fullName.trim() &&
    password.length >= PASSWORD_MIN;

  function submit(e: FormEvent) {
    e.preventDefault();
    if (isEdit) {
      const body: UserUpdate = {};
      if (email.trim() !== existing!.email) body.email = email.trim();
      if (fullName.trim() !== existing!.full_name) body.full_name = fullName.trim();
      // Self-role-change is prevented in the UI (convenience guard only).
      if (!isSelf && role !== existing!.role) body.role = role;
      if (Object.keys(body).length === 0) {
        onClose();
        return;
      }
      update.mutate(body, {
        onSuccess: () => {
          toast.success('User updated.');
          onClose();
        },
      });
    } else {
      const body: UserCreate = {
        username: username.trim(),
        email: email.trim(),
        full_name: fullName.trim(),
        role,
        password,
      };
      create.mutate(body, {
        onSuccess: () => {
          toast.success('User created.');
          onClose();
        },
      });
    }
  }

  return (
    <Modal title={isEdit ? 'Edit user' : 'New user'} onClose={onClose}>
      <form onSubmit={submit} className="space-y-3">
        {!isEdit && (
          <Field label="Username" htmlFor="user-username" required hint="At least 3 characters">
            <TextInput
              id="user-username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              minLength={3}
              maxLength={64}
              required
              autoFocus
            />
          </Field>
        )}
        <Field label="Full name" htmlFor="user-fullname" required>
          <TextInput
            id="user-fullname"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            maxLength={150}
            required
          />
        </Field>
        <Field label="Email" htmlFor="user-email" required>
          <TextInput
            id="user-email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </Field>
        <Field
          label="Role"
          htmlFor="user-role"
          required
          hint={isSelf ? 'You cannot change your own role.' : undefined}
        >
          <Select
            id="user-role"
            value={role}
            onChange={(e) => setRole(e.target.value as UserRole)}
            disabled={isSelf}
          >
            {USER_ROLES.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </Select>
        </Field>
        {!isEdit && (
          <Field
            label="Initial password"
            htmlFor="user-password"
            required
            hint={`At least ${PASSWORD_MIN} characters; must not equal the username or email.`}
          >
            <TextInput
              id="user-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              minLength={PASSWORD_MIN}
              maxLength={128}
              autoComplete="new-password"
              required
            />
          </Field>
        )}
        {error != null && <InlineError error={error} />}
        <div className="flex justify-end gap-2 pt-1">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" loading={pending} disabled={!isEdit && !createValid}>
            {isEdit ? 'Save changes' : 'Create user'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
