// Concept by MrHan (08974747477)
import '@testing-library/jest-dom/vitest';
import { afterAll, afterEach, beforeAll, beforeEach } from 'vitest';
import { server } from './server';
import { clearAccessToken } from '@/auth/tokenStore';

// jsdom does not implement Blob object-URL APIs used by file downloads. Provide
// deterministic stubs so download flows can run (tests spy on these as needed).
URL.createObjectURL = () => 'blob:mock';
URL.revokeObjectURL = () => {};

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));

beforeEach(() => {
  // Ensure the memory-only token store is empty between tests.
  clearAccessToken();
});

afterEach(() => server.resetHandlers());
afterAll(() => server.close());
