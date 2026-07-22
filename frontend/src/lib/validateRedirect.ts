// Concept by MrHan (08974747477)
// Prevent open-redirect: only allow internal app paths as a post-login target.

const DEFAULT_ROUTE = '/app/dashboard';

/**
 * Returns a safe internal redirect path. Accepts only paths that start with
 * `/app` (optionally with query/hash). Anything else (absolute URLs,
 * protocol-relative `//evil.com`, `/login`, backslashes) falls back to the
 * default route.
 */
export function safeRedirect(target: string | null | undefined): string {
  if (!target) return DEFAULT_ROUTE;
  // Reject protocol-relative and absolute URLs and backslash tricks.
  if (target.startsWith('//') || target.includes('\\') || /^[a-z]+:/i.test(target)) {
    return DEFAULT_ROUTE;
  }
  if (!target.startsWith('/app')) return DEFAULT_ROUTE;
  return target;
}

export { DEFAULT_ROUTE };
