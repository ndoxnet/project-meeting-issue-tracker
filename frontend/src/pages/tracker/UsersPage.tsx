// Concept by MrHan (08974747477)
import { useState } from 'react';
import { KeyRound, Plus } from 'lucide-react';
import { ApiError } from '@/api/errors';
import { useActivateUser, useUsers, type UserFilters } from '@/api/users';
import type { UserResponse } from '@/api/types';
import { useAuth } from '@/auth/useAuth';
import { usePageTitle } from '@/hooks/usePageTitle';
import { useToast } from '@/components/feedback/ToastProvider';
import { PageHeader } from '@/components/layout/PageHeader';
import { DataState } from '@/components/feedback/DataState';
import { Pagination } from '@/components/ui/Pagination';
import { Button } from '@/components/ui/Button';
import { RoleBadge } from '@/components/ui/RoleBadge';
import { Select, TextInput } from '@/components/ui/Field';
import { formatDateTime } from '@/lib/dates';
import { UserFormModal } from '@/features/users/UserFormModal';
import { ResetPasswordModal } from '@/features/users/ResetPasswordModal';
import { DeactivateUserDialog } from '@/features/users/DeactivateUserDialog';

type StatusFilter = 'all' | 'active' | 'inactive';
type Dialog =
  | { mode: 'create' }
  | { mode: 'edit'; user: UserResponse }
  | { mode: 'deactivate'; user: UserResponse }
  | { mode: 'reset'; user: UserResponse }
  | null;

export function UsersPage() {
  usePageTitle('Users');
  const { user: currentUser } = useAuth();
  const [status, setStatus] = useState<StatusFilter>('all');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [dialog, setDialog] = useState<Dialog>(null);

  const filters: UserFilters = {
    page,
    page_size: 20,
    is_active: status === 'all' ? undefined : status === 'active',
    search: search || undefined,
  };
  const users = useUsers(filters);

  return (
    <section>
      <PageHeader
        title="Users"
        description="Manage accounts, roles, and access."
        actions={
          <Button type="button" onClick={() => setDialog({ mode: 'create' })}>
            <Plus className="h-4 w-4" aria-hidden="true" /> New user
          </Button>
        }
      />

      <div className="mb-3 flex flex-wrap items-center gap-2">
        <TextInput
          defaultValue={search}
          placeholder="Search name, username, email…"
          className="mt-0 max-w-xs"
          aria-label="Search users"
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              setPage(1);
              setSearch((e.target as HTMLInputElement).value.trim());
            }
          }}
        />
        <Select
          value={status}
          onChange={(e) => {
            setPage(1);
            setStatus(e.target.value as StatusFilter);
          }}
          className="mt-0 max-w-[10rem]"
          aria-label="Filter users by status"
        >
          <option value="all">All</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </Select>
      </div>

      <DataState
        isLoading={users.isLoading}
        error={users.error}
        isEmpty={(users.data?.items.length ?? 0) === 0}
        loadingLabel="Loading users…"
        emptyTitle="No users found"
        emptyDescription="Adjust the filters or create a new user."
      >
        <ul className="divide-y divide-border rounded-lg border border-border">
          {users.data?.items.map((u) => (
            <UserRow
              key={u.id}
              user={u}
              isSelf={u.id === currentUser?.id}
              onEdit={() => setDialog({ mode: 'edit', user: u })}
              onDeactivate={() => setDialog({ mode: 'deactivate', user: u })}
              onReset={() => setDialog({ mode: 'reset', user: u })}
            />
          ))}
        </ul>
        {users.data && <Pagination meta={users.data.meta} onPageChange={setPage} />}
      </DataState>

      {dialog?.mode === 'create' && <UserFormModal onClose={() => setDialog(null)} />}
      {dialog?.mode === 'edit' && (
        <UserFormModal
          existing={dialog.user}
          isSelf={dialog.user.id === currentUser?.id}
          onClose={() => setDialog(null)}
        />
      )}
      {dialog?.mode === 'deactivate' && (
        <DeactivateUserDialog user={dialog.user} onClose={() => setDialog(null)} />
      )}
      {dialog?.mode === 'reset' && (
        <ResetPasswordModal user={dialog.user} onClose={() => setDialog(null)} />
      )}
    </section>
  );
}

function UserRow({
  user,
  isSelf,
  onEdit,
  onDeactivate,
  onReset,
}: {
  user: UserResponse;
  isSelf: boolean;
  onEdit: () => void;
  onDeactivate: () => void;
  onReset: () => void;
}) {
  const toast = useToast();
  const activate = useActivateUser();

  function onActivate() {
    activate.mutate(user.id, {
      onSuccess: () => toast.success(`${user.username} activated.`),
      onError: (err) =>
        toast.error(err instanceof ApiError ? err.message : 'Could not activate the user.'),
    });
  }

  return (
    <li className="flex flex-wrap items-center gap-3 p-3">
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <span className="truncate text-sm font-medium text-text">{user.full_name}</span>
          <RoleBadge role={user.role} />
          {user.is_active ? (
            <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800">
              Active
            </span>
          ) : (
            <span className="rounded-full bg-slate-200 px-2 py-0.5 text-xs font-medium text-slate-700">
              Inactive
            </span>
          )}
          {isSelf && <span className="text-xs text-muted">(you)</span>}
        </div>
        <p className="truncate text-xs text-muted">
          @{user.username} · {user.email} ·{' '}
          {user.last_login_at ? `last login ${formatDateTime(user.last_login_at)}` : 'never logged in'}
        </p>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <Button type="button" variant="secondary" onClick={onEdit}>
          Edit
        </Button>
        <Button type="button" variant="ghost" onClick={onReset}>
          <KeyRound className="h-4 w-4" aria-hidden="true" /> Reset password
        </Button>
        {user.is_active ? (
          <Button
            type="button"
            variant="ghost"
            onClick={onDeactivate}
            disabled={isSelf}
            title={isSelf ? 'You cannot deactivate your own account' : undefined}
          >
            Deactivate
          </Button>
        ) : (
          <Button type="button" variant="ghost" loading={activate.isPending} onClick={onActivate}>
            Activate
          </Button>
        )}
      </div>
    </li>
  );
}
