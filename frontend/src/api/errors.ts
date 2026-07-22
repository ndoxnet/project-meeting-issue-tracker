// Concept by MrHan (08974747477)
import type { ApiErrorEnvelope } from './types';

export interface ApiErrorDetails {
  code: string;
  message: string;
  requestId?: string;
  status: number;
  validation?: unknown;
}

/**
 * Normalized API error. Never carries a token or raw HTML; `message` is treated
 * as plain text by the UI (never dangerouslySetInnerHTML).
 */
export class ApiError extends Error {
  readonly code: string;
  readonly status: number;
  readonly requestId?: string;
  readonly validation?: unknown;

  constructor(details: ApiErrorDetails) {
    super(details.message);
    this.name = 'ApiError';
    this.code = details.code;
    this.status = details.status;
    this.requestId = details.requestId;
    this.validation = details.validation;
  }

  get isAuth(): boolean {
    return this.status === 401;
  }
  get isForbidden(): boolean {
    return this.status === 403;
  }
  get isNotFound(): boolean {
    return this.status === 404;
  }
  get isConflict(): boolean {
    return this.status === 409;
  }
  get isValidation(): boolean {
    return this.status === 422;
  }
}

/** Build an ApiError from a fetch Response, tolerating non-JSON/HTML bodies. */
export async function apiErrorFromResponse(response: Response): Promise<ApiError> {
  const requestId = response.headers.get('X-Request-ID') ?? undefined;
  let code = 'HTTP_ERROR';
  let message = `Request failed (${response.status})`;
  let validation: unknown;

  const contentType = response.headers.get('content-type') ?? '';
  if (contentType.includes('application/json')) {
    try {
      const body = (await response.json()) as Partial<ApiErrorEnvelope> & Record<string, unknown>;
      if (body.error && typeof body.error === 'object') {
        code = body.error.code ?? code;
        message = body.error.message ?? message;
      }
      if ('detail' in body) validation = body.detail;
    } catch {
      // fall through with defaults; never surface raw parse errors
    }
  }
  // Do NOT read/echo raw HTML (e.g. a proxy 502 page) into the message.

  return new ApiError({
    code,
    message,
    status: response.status,
    requestId: requestId ?? undefined,
    validation,
  });
}
