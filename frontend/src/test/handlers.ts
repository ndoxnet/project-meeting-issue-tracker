// Concept by MrHan (08974747477)
// MSW handlers modeling the frozen v1 auth contract for tests.
import { http, HttpResponse } from 'msw';
import type { CurrentUser, UserRole } from '@/api/types';

const BASE = '/api/v1';

export function makeUser(role: UserRole, username = role.toLowerCase()): CurrentUser {
  return {
    id: `00000000-0000-4000-8000-0000000000${role.length}`,
    full_name: `${role} User`,
    email: `${username}@example.invalid`,
    username,
    role,
    is_active: true,
    last_login_at: null,
    created_at: '2026-07-20T00:00:00Z',
    updated_at: '2026-07-20T00:00:00Z',
  };
}

// Test credentials: password must be "correct-password".
const CREDENTIALS: Record<string, UserRole> = {
  admin1: 'ADMIN',
  editor1: 'EDITOR',
  viewer1: 'VIEWER',
};

function errorEnvelope(code: string, message: string) {
  return HttpResponse.json({ error: { code, message, request_id: 'test-req-id' } }, {
    status: code === 'AUTHENTICATION_FAILED' ? 401 : 400,
    headers: { 'X-Request-ID': 'test-req-id' },
  });
}

export const handlers = [
  http.post(`${BASE}/auth/login`, async ({ request }) => {
    const body = (await request.json()) as { username: string; password: string };
    const role = CREDENTIALS[body.username];
    if (!role || body.password !== 'correct-password') {
      return errorEnvelope('AUTHENTICATION_FAILED', 'Invalid credentials');
    }
    const user = makeUser(role, body.username);
    return HttpResponse.json(
      { access_token: `test-token-${role}`, token_type: 'bearer', expires_in: 28800, user },
      { headers: { 'X-Request-ID': 'test-req-id' } },
    );
  }),

  http.get(`${BASE}/auth/me`, ({ request }) => {
    const auth = request.headers.get('Authorization') ?? '';
    const match = /^Bearer test-token-(ADMIN|EDITOR|VIEWER)$/.exec(auth);
    if (!match) return errorEnvelope('AUTHENTICATION_FAILED', 'Not authenticated');
    return HttpResponse.json(makeUser(match[1] as UserRole));
  }),

  http.post(`${BASE}/auth/logout`, () =>
    HttpResponse.json({ message: 'Logged out.' }, { headers: { 'X-Request-ID': 'test-req-id' } }),
  ),
];
