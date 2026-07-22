// Concept by MrHan (08974747477)
// Canonical route paths (single source of truth for links/redirects).
export const ROUTES = {
  login: '/login',
  forbidden: '/forbidden',
  app: '/app',
  dashboard: '/app/dashboard',
  issues: '/app/issues',
  meetings: '/app/meetings',
  reports: '/app/reports',
  users: '/app/users',
  audit: '/app/audit',
  settings: '/app/settings',
} as const;
