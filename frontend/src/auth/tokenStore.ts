// Concept by MrHan (08974747477)
// Memory-only access token store (ADR-017). The token lives ONLY in this module
// closure — never localStorage, sessionStorage, IndexedDB, or cookies. A browser
// refresh clears it (module re-evaluates), forcing re-login. Never logged.

let accessToken: string | null = null;
const listeners = new Set<() => void>();

function emit(): void {
  listeners.forEach((l) => l());
}

export function getAccessToken(): string | null {
  return accessToken;
}

export function setAccessToken(token: string): void {
  accessToken = token;
  emit();
}

export function clearAccessToken(): void {
  accessToken = null;
  emit();
}

export function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}
