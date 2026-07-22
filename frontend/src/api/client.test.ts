// Concept by MrHan (08974747477)
import { afterEach, describe, expect, it, vi } from 'vitest';
import { http, HttpResponse } from 'msw';
import { server } from '@/test/server';
import { apiClient, setUnauthorizedHandler } from './client';
import { setAccessToken, clearAccessToken } from '@/auth/tokenStore';
import { ApiError } from './errors';

const BASE = '/api/v1';

afterEach(() => {
  clearAccessToken();
  setUnauthorizedHandler(null);
});

describe('apiClient', () => {
  it('attaches the bearer token when present', async () => {
    let seen: string | null = null;
    server.use(
      http.get(`${BASE}/probe`, ({ request }) => {
        seen = request.headers.get('Authorization');
        return HttpResponse.json({ ok: true });
      }),
    );
    setAccessToken('tok123');
    await apiClient.get('/probe');
    expect(seen).toBe('Bearer tok123');
  });

  it('sends no Authorization header without a token', async () => {
    let seen: string | null = 'x';
    server.use(
      http.get(`${BASE}/probe`, ({ request }) => {
        seen = request.headers.get('Authorization');
        return HttpResponse.json({ ok: true });
      }),
    );
    await apiClient.get('/probe');
    expect(seen).toBeNull();
  });

  it('parses JSON responses', async () => {
    server.use(http.get(`${BASE}/probe`, () => HttpResponse.json({ value: 42 })));
    const data = await apiClient.get<{ value: number }>('/probe');
    expect(data.value).toBe(42);
  });

  it('supports empty/void responses', async () => {
    server.use(http.post(`${BASE}/void`, () => new HttpResponse(null, { status: 204 })));
    const data = await apiClient.post<void>('/void', { parse: 'void' });
    expect(data).toBeUndefined();
  });

  it('does NOT set Content-Type for FormData uploads', async () => {
    let ct: string | null = null;
    server.use(
      http.post(`${BASE}/upload`, ({ request }) => {
        ct = request.headers.get('Content-Type');
        return HttpResponse.json({ ok: true });
      }),
    );
    const fd = new FormData();
    fd.append('file', new Blob(['x']), 'a.pdf');
    await apiClient.post('/upload', { formData: fd });
    expect(ct).toContain('multipart/form-data'); // set by the browser, not by us
  });

  it('normalizes API errors and captures the request id', async () => {
    server.use(
      http.get(`${BASE}/boom`, () =>
        HttpResponse.json(
          { error: { code: 'ISSUE_NOT_FOUND', message: 'Issue not found', request_id: 'rid-9' } },
          { status: 404, headers: { 'X-Request-ID': 'rid-9' } },
        ),
      ),
    );
    await expect(apiClient.get('/boom')).rejects.toMatchObject({
      code: 'ISSUE_NOT_FOUND',
      status: 404,
      requestId: 'rid-9',
    });
  });

  it('invokes the unauthorized handler on 401 and error carries no token', async () => {
    const onUnauth = vi.fn();
    setUnauthorizedHandler(onUnauth);
    setAccessToken('sekret');
    server.use(
      http.get(`${BASE}/secure`, () =>
        HttpResponse.json({ error: { code: 'AUTHENTICATION_FAILED', message: 'no' } }, { status: 401 }),
      ),
    );
    const err = (await apiClient.get('/secure').catch((e) => e)) as ApiError;
    expect(onUnauth).toHaveBeenCalledOnce();
    expect(err).toBeInstanceOf(ApiError);
    expect(JSON.stringify({ ...err, message: err.message })).not.toContain('sekret');
  });
});
