// Concept by MrHan (08974747477)
// Typed, fail-fast environment config. Contains NO secrets. The access token is
// never a build-time value.

function required(value: string | undefined, name: string, fallback?: string): string {
  const v = value ?? fallback;
  if (v === undefined || v === '') {
    throw new Error(`Missing required frontend env var: ${name}`);
  }
  return v;
}

const apiBaseUrl = required(import.meta.env.VITE_API_BASE_URL, 'VITE_API_BASE_URL', '/api/v1');

// Basic validation: must be a relative /api path or an absolute http(s) URL.
if (!/^\/|^https?:\/\//.test(apiBaseUrl)) {
  throw new Error(`Invalid VITE_API_BASE_URL: ${apiBaseUrl}`);
}

export const env = {
  apiBaseUrl,
  appName: required(import.meta.env.VITE_APP_NAME, 'VITE_APP_NAME', 'Project Meeting Issue Tracker'),
  appVersion: required(import.meta.env.VITE_APP_VERSION, 'VITE_APP_VERSION', '0.3.0'),
} as const;
