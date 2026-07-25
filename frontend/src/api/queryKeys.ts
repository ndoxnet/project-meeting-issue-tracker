// Concept by MrHan (08974747477)
// Centralized, stable TanStack Query keys (avoids duplicate fetches from unstable
// references). Filter objects are serialized by React Query structurally.
export const queryKeys = {
  auth: {
    me: ['auth', 'me'] as const,
  },
  dashboard: {
    summary: ['dashboard', 'summary'] as const,
    recentlyUpdated: (limit: number) => ['dashboard', 'recently-updated', limit] as const,
    overdue: (limit: number) => ['dashboard', 'overdue', limit] as const,
    stagnant: (limit: number) => ['dashboard', 'stagnant', limit] as const,
    dueThisWeek: (limit: number) => ['dashboard', 'due-this-week', limit] as const,
    byCategory: ['dashboard', 'by-category'] as const,
    byResponsibleParty: ['dashboard', 'by-responsible-party'] as const,
    openedVsClosed: (months: number) => ['dashboard', 'opened-vs-closed', months] as const,
  },
  meetings: {
    types: ['meeting-types'] as const,
    occurrences: (filters: unknown) => ['meeting-occurrences', filters] as const,
    occurrence: (id: string) => ['meeting-occurrence', id] as const,
  },
  issues: {
    list: (filters: unknown) => ['issues', filters] as const,
    detail: (id: string) => ['issue', id] as const,
    updates: (id: string) => ['issue', id, 'updates'] as const,
    attachments: (id: string) => ['issue', id, 'attachments'] as const,
  },
  master: {
    categories: ['master', 'categories'] as const,
    responsibleParties: ['master', 'responsible-parties'] as const,
  },
} as const;
