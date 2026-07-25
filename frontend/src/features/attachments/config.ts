// Concept by MrHan (08974747477)
// Attachment client-side constraints. These MIRROR the backend authoritative
// configuration (backend/app/core/config.py: ATTACHMENT_MAX_MB default 10 and
// ATTACHMENT_ALLOWED_TYPES). The backend remains the sole authority — these are
// usability pre-checks only, so a rejected file never reaches the network.

export const ATTACHMENT_MAX_MB = 10;
export const ATTACHMENT_MAX_BYTES = ATTACHMENT_MAX_MB * 1024 * 1024;

/** Allowed MIME types (canonical set from the backend allow-list). */
export const ATTACHMENT_ALLOWED_MIME = ['application/pdf', 'image/jpeg', 'image/png'] as const;

/** `accept` attribute for the file input (advisory; backend validates content). */
export const ATTACHMENT_ACCEPT = '.pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png';

/** Human-readable byte size, e.g. 1536 -> "1.5 KB". */
export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  const units = ['KB', 'MB', 'GB'];
  let value = bytes / 1024;
  let unit = 0;
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024;
    unit += 1;
  }
  return `${value.toFixed(value >= 10 || Number.isInteger(value) ? 0 : 1)} ${units[unit]}`;
}

export type AttachmentPrecheck = { ok: true } | { ok: false; reason: string };

/**
 * Usability pre-check before upload. NOT authoritative — the backend re-validates
 * size, declared type, and magic-byte signature and is the final word.
 */
export function precheckAttachment(file: File): AttachmentPrecheck {
  if (file.size > ATTACHMENT_MAX_BYTES) {
    return {
      ok: false,
      reason: `File is ${formatBytes(file.size)}; the maximum is ${ATTACHMENT_MAX_MB} MB.`,
    };
  }
  // Some browsers leave file.type empty; only reject when a type IS declared and
  // it is clearly outside the allow-list (the backend still checks the content).
  if (file.type && !ATTACHMENT_ALLOWED_MIME.includes(file.type as (typeof ATTACHMENT_ALLOWED_MIME)[number])) {
    return { ok: false, reason: 'Only PDF, JPEG, or PNG files are allowed.' };
  }
  return { ok: true };
}
