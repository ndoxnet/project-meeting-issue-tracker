// Concept by MrHan (08974747477)
import { describe, expect, it } from 'vitest';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { server } from '@/test/server';
import { renderWithProviders } from '@/test/utils';
import { makeIssueUpdate } from '@/test/trackerHandlers';
import { Timeline } from './Timeline';

const BASE = '/api/v1';

describe('VoidUpdateButton (via Timeline)', () => {
  it('is hidden when the viewer cannot void', () => {
    renderWithProviders(
      <Timeline updates={[makeIssueUpdate()]} issueId="iss-1" canVoid={false} />,
    );
    expect(screen.queryByRole('button', { name: 'Void' })).not.toBeInTheDocument();
  });

  it('voids an update with a required reason and an irreversible warning', async () => {
    let sentReason: string | null = null;
    server.use(
      http.post(`${BASE}/issues/:id/updates/:uid/void`, async ({ request }) => {
        sentReason = ((await request.json()) as { void_reason: string }).void_reason;
        return HttpResponse.json({
          update: makeIssueUpdate({ voided_at: '2026-07-20T00:00:00Z', void_reason: sentReason ?? '' }),
          warnings: [],
        });
      }),
    );
    const user = userEvent.setup();
    renderWithProviders(<Timeline updates={[makeIssueUpdate()]} issueId="iss-1" canVoid />);

    await user.click(screen.getByRole('button', { name: 'Void' }));
    expect(screen.getByText(/permanently voids/i)).toBeInTheDocument();
    await user.type(screen.getByLabelText(/reason/i), 'Duplicate entry');
    await user.click(screen.getByRole('button', { name: /void update/i }));

    expect(await screen.findByText(/Follow-up update voided/i)).toBeInTheDocument();
    expect(sentReason).toBe('Duplicate entry');
  });

  it('preserves the reason after a recoverable error', async () => {
    server.use(
      http.post(`${BASE}/issues/:id/updates/:uid/void`, () =>
        HttpResponse.json({ error: { code: 'CONFLICT', message: 'Already voided' } }, { status: 409 }),
      ),
    );
    const user = userEvent.setup();
    renderWithProviders(<Timeline updates={[makeIssueUpdate()]} issueId="iss-1" canVoid />);

    await user.click(screen.getByRole('button', { name: 'Void' }));
    await user.type(screen.getByLabelText(/reason/i), 'My reason');
    await user.click(screen.getByRole('button', { name: /void update/i }));

    expect(await screen.findByText(/Already voided/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/reason/i)).toHaveValue('My reason');
  });
});
