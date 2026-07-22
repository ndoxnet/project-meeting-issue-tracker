// Concept by MrHan (08974747477)
import { describe, expect, it } from 'vitest';
import { safeRedirect, DEFAULT_ROUTE } from './validateRedirect';

describe('safeRedirect (open-redirect prevention)', () => {
  it('allows internal /app paths', () => {
    expect(safeRedirect('/app/issues?status=OPEN')).toBe('/app/issues?status=OPEN');
  });

  it('falls back to default for empty/null', () => {
    expect(safeRedirect(null)).toBe(DEFAULT_ROUTE);
    expect(safeRedirect('')).toBe(DEFAULT_ROUTE);
  });

  it('rejects absolute and protocol-relative URLs', () => {
    expect(safeRedirect('https://evil.com')).toBe(DEFAULT_ROUTE);
    expect(safeRedirect('//evil.com')).toBe(DEFAULT_ROUTE);
    expect(safeRedirect('javascript:alert(1)')).toBe(DEFAULT_ROUTE);
    expect(safeRedirect('/\\evil.com')).toBe(DEFAULT_ROUTE);
  });

  it('rejects non-/app internal paths', () => {
    expect(safeRedirect('/login')).toBe(DEFAULT_ROUTE);
    expect(safeRedirect('/etc/passwd')).toBe(DEFAULT_ROUTE);
  });
});
