// Concept by MrHan (08974747477)
// Shared domain types. Placeholder shapes for Phase 1 — refined in Phase 2/3 to
// match the backend Pydantic schemas exactly.

export type UserRole = 'ADMIN' | 'EDITOR' | 'VIEWER';

export type IssuePriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type IssueStatus =
  | 'OPEN'
  | 'IN_PROGRESS'
  | 'PENDING'
  | 'CLOSED'
  | 'REOPENED';

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

// Minimal placeholders (full fields added in Phase 3).
export interface IssueSummary {
  id: string;
  issue_code: string;
  title: string;
  priority: IssuePriority;
  status: IssueStatus;
  due_date: string | null;
}
