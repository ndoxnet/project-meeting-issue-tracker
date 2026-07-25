// Concept by MrHan (08974747477)
// Date formatting. Date-only fields (YYYY-MM-DD) are shown verbatim (no timezone
// shift). Timestamps (date-time, UTC) are shown in the display timezone.
const DISPLAY_TZ = 'Asia/Jakarta';
const DATE_ONLY = /^(\d{4})-(\d{2})-(\d{2})$/;

/** Format a date-only ("YYYY-MM-DD") or fall back to a locale date. Never shifts a date-only value. */
export function formatDate(value: string | null | undefined): string {
  if (!value) return '—';
  const m = DATE_ONLY.exec(value);
  if (m) return `${m[3]}/${m[2]}/${m[1]}`; // dd/mm/yyyy, no tz math
  const dt = new Date(value);
  return Number.isNaN(dt.getTime())
    ? '—'
    : dt.toLocaleDateString('en-GB', { timeZone: DISPLAY_TZ });
}

/** Format a UTC timestamp for display in the app timezone. */
export function formatDateTime(value: string | null | undefined): string {
  if (!value) return '—';
  const dt = new Date(value);
  return Number.isNaN(dt.getTime())
    ? '—'
    : dt.toLocaleString('en-GB', { timeZone: DISPLAY_TZ });
}
