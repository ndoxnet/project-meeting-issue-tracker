// Concept by MrHan (08974747477)
import '@testing-library/jest-dom/vitest';
import { afterAll, afterEach, beforeAll, beforeEach } from 'vitest';
import { server } from './server';
import { clearAccessToken } from '@/auth/tokenStore';

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));

beforeEach(() => {
  // Ensure the memory-only token store is empty between tests.
  clearAccessToken();
});

afterEach(() => server.resetHandlers());
afterAll(() => server.close());
