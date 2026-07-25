// Concept by MrHan (08974747477)
// Domain type aliases DERIVED from the generated OpenAPI schema (ADR-019).
// The generated schema (src/api/generated/schema.ts) is the contract authority;
// these are readable names for the components used across the app. Do not
// hand-duplicate backend DTO shapes here.
import type { components } from './generated/schema';

type S = components['schemas'];

// ---- enums ----
export type UserRole = S['UserRole'];
export type IssueStatus = S['IssueStatus'];
export type IssuePriority = S['IssuePriority'];

// ---- auth ----
export type CurrentUser = S['UserResponse'];
export type LoginInput = S['LoginRequest'];
export type TokenResponse = S['TokenResponse'];

// ---- user administration ----
export type UserResponse = S['UserResponse'];
export type UserCreate = S['UserCreate'];
export type UserUpdate = S['UserUpdate'];
export type PasswordResetRequest = S['PasswordResetRequest'];

// ---- app settings (read-only) ----
export type AppSettingResponse = S['AppSettingResponse'];

// ---- generic ----
export type Message = S['Message'];

// ---- errors ----
export type ApiErrorBody = S['ErrorBody'];
export type ApiErrorEnvelope = S['ErrorResponse'];

// ---- pagination ----
export type PageMeta = S['PageMeta'];
export interface Page<T> {
  items: T[];
  meta: PageMeta;
}

// ---- master data ----
export type NamedResponse = S['NamedResponse'];
export type NamedCreate = S['NamedCreate'];
export type NamedUpdate = S['NamedUpdate'];
export type MeetingOccurrence = S['MeetingOccurrenceResponse'];
export type MeetingOccurrenceCreate = S['MeetingOccurrenceCreate'];
export type MeetingOccurrenceUpdate = S['MeetingOccurrenceUpdate'];

// ---- issues ----
export type IssueListItem = S['IssueListItem'];
export type IssueDetailResponse = S['IssueDetailResponse'];
export type IssueCreate = S['IssueCreate'];
export type IssueMetadataUpdate = S['IssueMetadataUpdate'];
export type IssueCreateResponse = S['IssueCreateResponse'];
export type DuplicateWarning = S['DuplicateWarning'];
export type IssueStatusChangeRequest = S['IssueStatusChangeRequest'];
export type IssueCloseRequest = S['IssueCloseRequest'];
export type IssueReopenRequest = S['IssueReopenRequest'];
export type IssueUpdateCreate = S['IssueUpdateCreate'];
export type IssueUpdateResponse = S['IssueUpdateResponse'];
export type IssueUpdateVoidRequest = S['IssueUpdateVoidRequest'];
export type VoidResponse = S['VoidResponse'];

// ---- attachments ----
export type AttachmentResponse = S['AttachmentResponse'];

// ---- dashboard ----
export type DashboardSummary = S['DashboardSummary'];
export type CountByLabel = S['CountByLabel'];
export type MonthlyTrendPoint = S['MonthlyTrendPoint'];

// ---- constants (from the frozen enums) ----
export const ISSUE_STATUSES: IssueStatus[] = [
  'OPEN',
  'IN_PROGRESS',
  'PENDING',
  'CLOSED',
  'REOPENED',
];
export const ISSUE_PRIORITIES: IssuePriority[] = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];
export const USER_ROLES: UserRole[] = ['ADMIN', 'EDITOR', 'VIEWER'];
