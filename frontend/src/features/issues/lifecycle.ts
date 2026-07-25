// Concept by MrHan (08974747477)
// UI mirror of the backend issue lifecycle (ADR-012) for gating action buttons.
// The backend remains authoritative — the UI only avoids offering transitions the
// server will reject.
import type { IssueStatus } from '@/api/types';

// Valid targets for the generic /status endpoint (excludes CLOSED — use Close;
// excludes any transition out of CLOSED — use Reopen).
const STATUS_TRANSITIONS: Record<IssueStatus, IssueStatus[]> = {
  OPEN: ['IN_PROGRESS', 'PENDING'],
  IN_PROGRESS: ['PENDING', 'OPEN'],
  PENDING: ['IN_PROGRESS', 'OPEN'],
  CLOSED: [],
  REOPENED: ['IN_PROGRESS', 'PENDING'],
};

export function allowedStatusTargets(current: IssueStatus): IssueStatus[] {
  return STATUS_TRANSITIONS[current] ?? [];
}

export function canClose(status: IssueStatus): boolean {
  return status !== 'CLOSED';
}

export function canReopen(status: IssueStatus): boolean {
  return status === 'CLOSED';
}

export function canEditMetadata(status: IssueStatus, isArchived: boolean): boolean {
  // Backend rejects metadata edits on CLOSED or archived issues.
  return status !== 'CLOSED' && !isArchived;
}
