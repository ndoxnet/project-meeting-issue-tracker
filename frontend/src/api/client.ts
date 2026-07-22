// Concept by MrHan (08974747477)
// Framework-agnostic typed fetch client. Attaches the in-memory bearer token,
// normalizes errors, and invokes an unauthorized handler on 401. It never logs
// the token, never puts it in the URL, and never persists it.
import { env } from '@/config/env';
import { getAccessToken } from '@/auth/tokenStore';
import { apiErrorFromResponse } from './errors';

type Unauthorized = () => void;
let onUnauthorized: Unauthorized | null = null;

/** Register the callback fired on any 401 (clears session, redirects to login). */
export function setUnauthorizedHandler(handler: Unauthorized | null): void {
  onUnauthorized = handler;
}

export interface RequestOptions {
  method?: string;
  /** JSON-serializable body. Omit for GET. Mutually exclusive with `formData`. */
  json?: unknown;
  /** Multipart upload; Content-Type is set by the browser (do NOT set manually). */
  formData?: FormData;
  query?: Record<string, string | number | boolean | undefined | (string | number)[]>;
  signal?: AbortSignal;
  /** 'json' (default), 'blob' (downloads), 'text' (CSV), or 'void' (empty body). */
  parse?: 'json' | 'blob' | 'text' | 'void';
}

function buildUrl(path: string, query?: RequestOptions['query']): string {
  const base = env.apiBaseUrl.replace(/\/$/, '');
  const url = `${base}${path}`;
  if (!query) return url;
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value === undefined) continue;
    if (Array.isArray(value)) value.forEach((v) => params.append(key, String(v)));
    else params.append(key, String(value));
  }
  const qs = params.toString();
  return qs ? `${url}?${qs}` : url;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', json, formData, query, signal, parse = 'json' } = options;

  const headers: Record<string, string> = { Accept: 'application/json' };
  const token = getAccessToken();
  if (token) headers.Authorization = `Bearer ${token}`; // never logged

  let body: BodyInit | undefined;
  if (formData) {
    body = formData; // browser sets multipart Content-Type + boundary
  } else if (json !== undefined) {
    headers['Content-Type'] = 'application/json';
    body = JSON.stringify(json);
  }

  const response = await fetch(buildUrl(path, query), { method, headers, body, signal });

  if (response.status === 401) {
    onUnauthorized?.();
    throw await apiErrorFromResponse(response);
  }
  if (!response.ok) {
    throw await apiErrorFromResponse(response);
  }

  if (parse === 'void' || response.status === 204) return undefined as T;
  if (parse === 'blob') return (await response.blob()) as T;
  if (parse === 'text') return (await response.text()) as T;

  const text = await response.text();
  return (text ? JSON.parse(text) : undefined) as T;
}

export const apiClient = {
  request,
  get: <T>(path: string, options?: Omit<RequestOptions, 'method' | 'json' | 'formData'>) =>
    request<T>(path, { ...options, method: 'GET' }),
  post: <T>(path: string, options?: Omit<RequestOptions, 'method'>) =>
    request<T>(path, { ...options, method: 'POST' }),
  patch: <T>(path: string, options?: Omit<RequestOptions, 'method'>) =>
    request<T>(path, { ...options, method: 'PATCH' }),
};
