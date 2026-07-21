// Concept by MrHan (08974747477)
// Presentation helpers. Timestamps arrive as UTC ISO strings; display uses the
// app timezone (Asia/Jakarta). Full i18n/formatting refined in Phase 3.

const DISPLAY_TZ = 'Asia/Jakarta';

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return '-';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '-';
  return d.toLocaleDateString('id-ID', { timeZone: DISPLAY_TZ });
}

export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return '-';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '-';
  return d.toLocaleString('id-ID', { timeZone: DISPLAY_TZ });
}
