// Concept by MrHan (08974747477)
// Readable domain type aliases sourced from the frozen v1 OpenAPI contract
// (docs/api/openapi.json). These are hand-authored per ADR-019 for the types the
// app uses directly; broader coverage comes from the generated schema
// (src/api/generated/schema.ts) via openapi-typescript, generated off-VPS.
//
// Keep these in sync with the contract; the drift guard is `npm run check:api`.

export type UserRole = 'ADMIN' | 'EDITOR' | 'VIEWER';

export type IssueStatus = 'OPEN' | 'IN_PROGRESS' | 'PENDING' | 'CLOSED' | 'REOPENED';

export type IssuePriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

/** UserResponse (no password field is ever present). */
export interface CurrentUser {
  id: string;
  full_name: string;
  email: string;
  username: string;
  role: UserRole;
  is_active: boolean;
  last_login_at: string | null;
  created_at: string;
  updated_at: string;
}

/** LoginRequest body. `username` accepts a username or an email. */
export interface LoginInput {
  username: string;
  password: string;
}

/** TokenResponse. The access token is used transiently and never persisted. */
export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: CurrentUser;
}

/** Standard error envelope: { error: { code, message, request_id } }. */
export interface ApiErrorBody {
  code: string;
  message: string;
  request_id?: string | null;
}

export interface ApiErrorEnvelope {
  error: ApiErrorBody;
}

/** PageMeta / Page<T> pagination shape. */
export interface PageMeta {
  page: number;
  page_size: number;
  total: number;
  pages: number;
}

export interface Page<T> {
  items: T[];
  meta: PageMeta;
}
