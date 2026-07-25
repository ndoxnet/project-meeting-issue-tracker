// Concept by MrHan (08974747477)
import { useState } from 'react';
import { Plus } from 'lucide-react';
import { ApiError } from '@/api/errors';
import {
  useActivateNamed,
  useDeactivateNamed,
  useNamedList,
  type NamedListFilters,
  type NamedResourceKind,
} from '@/api/masterdataAdmin';
import type { NamedResponse } from '@/api/types';
import { useToast } from '@/components/feedback/ToastProvider';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { Select, TextInput } from '@/components/ui/Field';
import { DataState } from '@/components/feedback/DataState';
import { InlineError } from '@/components/feedback/InlineError';
import { Pagination } from '@/components/ui/Pagination';
import { NamedFormModal } from './NamedFormModal';

type StatusFilter = 'all' | 'active' | 'inactive';
type Dialog =
  | { mode: 'create' }
  | { mode: 'edit'; item: NamedResponse }
  | { mode: 'deactivate'; item: NamedResponse }
  | null;

/** Admin management for one named master-data resource. */
export function NamedResourceManager({
  kind,
  singular,
}: {
  kind: NamedResourceKind;
  singular: string;
}) {
  const [status, setStatus] = useState<StatusFilter>('all');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [dialog, setDialog] = useState<Dialog>(null);

  const filters: NamedListFilters = {
    page,
    page_size: 50,
    is_active: status === 'all' ? undefined : status === 'active',
    search: search || undefined,
  };
  const list = useNamedList(kind, filters);

  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <TextInput
          defaultValue={search}
          placeholder={`Search ${singular.toLowerCase()}…`}
          className="mt-0 max-w-xs"
          aria-label={`Search ${singular.toLowerCase()}`}
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
          aria-label={`Filter ${singular.toLowerCase()} by status`}
        >
          <option value="all">All</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </Select>
        <Button type="button" className="ml-auto" onClick={() => setDialog({ mode: 'create' })}>
          <Plus className="h-4 w-4" aria-hidden="true" /> New {singular.toLowerCase()}
        </Button>
      </div>

      <DataState
        isLoading={list.isLoading}
        error={list.error}
        isEmpty={(list.data?.items.length ?? 0) === 0}
        loadingLabel="Loading…"
        emptyTitle={`No ${singular.toLowerCase()} found`}
        emptyDescription="Adjust the filters or create a new record."
      >
        <ul className="divide-y divide-border rounded-lg border border-border">
          {list.data?.items.map((item) => (
            <Row
              key={item.id}
              kind={kind}
              singular={singular}
              item={item}
              onEdit={() => setDialog({ mode: 'edit', item })}
              onDeactivate={() => setDialog({ mode: 'deactivate', item })}
            />
          ))}
        </ul>
        {list.data && <Pagination meta={list.data.meta} onPageChange={setPage} />}
      </DataState>

      {dialog?.mode === 'create' && (
        <NamedFormModal kind={kind} singular={singular} onClose={() => setDialog(null)} />
      )}
      {dialog?.mode === 'edit' && (
        <NamedFormModal
          kind={kind}
          singular={singular}
          existing={dialog.item}
          onClose={() => setDialog(null)}
        />
      )}
      {dialog?.mode === 'deactivate' && (
        <DeactivateDialog
          kind={kind}
          singular={singular}
          item={dialog.item}
          onClose={() => setDialog(null)}
        />
      )}
    </div>
  );
}

function Row({
  kind,
  singular,
  item,
  onEdit,
  onDeactivate,
}: {
  kind: NamedResourceKind;
  singular: string;
  item: NamedResponse;
  onEdit: () => void;
  onDeactivate: () => void;
}) {
  const toast = useToast();
  const activate = useActivateNamed(kind);
  const [rowError, setRowError] = useState<unknown>(null);

  function onActivate() {
    setRowError(null);
    activate.mutate(item.id, {
      onSuccess: () => toast.success(`${singular} activated.`),
      onError: (err) => {
        setRowError(err);
        toast.error(err instanceof ApiError ? err.message : 'Could not activate.');
      },
    });
  }

  return (
    <li className="flex flex-wrap items-center gap-3 p-3">
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <span className="truncate text-sm font-medium text-text">{item.name}</span>
          {item.is_active ? (
            <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800">
              Active
            </span>
          ) : (
            <span className="rounded-full bg-slate-200 px-2 py-0.5 text-xs font-medium text-slate-700">
              Inactive
            </span>
          )}
        </div>
        {item.description && <p className="truncate text-xs text-muted">{item.description}</p>}
        {rowError != null && <InlineError error={rowError} className="mt-2" />}
      </div>
      <div className="flex items-center gap-2">
        <Button type="button" variant="secondary" onClick={onEdit}>
          Edit
        </Button>
        {item.is_active ? (
          <Button type="button" variant="ghost" onClick={onDeactivate}>
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

function DeactivateDialog({
  kind,
  singular,
  item,
  onClose,
}: {
  kind: NamedResourceKind;
  singular: string;
  item: NamedResponse;
  onClose: () => void;
}) {
  const toast = useToast();
  const deactivate = useDeactivateNamed(kind);

  function confirm() {
    deactivate.mutate(item.id, {
      onSuccess: () => {
        toast.success(`${singular} deactivated.`);
        onClose();
      },
      onError: (err) =>
        toast.error(err instanceof ApiError ? err.message : 'Could not deactivate.'),
    });
  }

  return (
    <Modal title={`Deactivate ${singular.toLowerCase()}`} onClose={onClose}>
      <p className="text-sm text-text">
        Deactivate <span className="font-medium">{item.name}</span>? This is{' '}
        <span className="font-medium">not a deletion</span>: it hides the record from pickers when
        creating new items. Existing issues and meetings keep their current value, and you can
        reactivate it later.
      </p>
      {deactivate.error != null && <InlineError error={deactivate.error} className="mt-3" />}
      <div className="mt-4 flex justify-end gap-2">
        <Button type="button" variant="ghost" onClick={onClose}>
          Cancel
        </Button>
        <Button type="button" loading={deactivate.isPending} onClick={confirm}>
          Deactivate
        </Button>
      </div>
    </Modal>
  );
}
