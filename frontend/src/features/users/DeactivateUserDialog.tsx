// Concept by MrHan (08974747477)
import { ApiError } from '@/api/errors';
import { useDeactivateUser } from '@/api/users';
import type { UserResponse } from '@/api/types';
import { useToast } from '@/components/feedback/ToastProvider';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { InlineError } from '@/components/feedback/InlineError';

export function DeactivateUserDialog({
  user,
  onClose,
}: {
  user: UserResponse;
  onClose: () => void;
}) {
  const toast = useToast();
  const deactivate = useDeactivateUser();

  function confirm() {
    deactivate.mutate(user.id, {
      onSuccess: () => {
        toast.success(`${user.username} deactivated.`);
        onClose();
      },
      onError: (err) =>
        toast.error(err instanceof ApiError ? err.message : 'Could not deactivate the user.'),
    });
  }

  return (
    <Modal title={`Deactivate ${user.username}`} onClose={onClose}>
      <p className="text-sm text-text">
        Deactivate <span className="font-medium">{user.username}</span>? They are signed out on
        their next request and cannot log in until reactivated. This is{' '}
        <span className="font-medium">not a deletion</span>.
      </p>
      {/* The backend refuses to deactivate the only active admin — shown inline here. */}
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
