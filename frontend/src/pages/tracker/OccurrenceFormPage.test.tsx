// Concept by MrHan (08974747477)
import { describe, expect, it } from 'vitest';
import { fireEvent, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Route, Routes } from 'react-router-dom';
import { http, HttpResponse } from 'msw';
import { server } from '@/test/server';
import { renderWithProviders } from '@/test/utils';
import { makeOccurrence } from '@/test/trackerHandlers';
import { OccurrenceFormPage } from './OccurrenceFormPage';

const BASE = '/api/v1';

function renderAt(entry: string) {
  return renderWithProviders(
    <Routes>
      <Route path="/app/meetings/new" element={<OccurrenceFormPage />} />
      <Route path="/app/meetings/:meetingId/edit" element={<OccurrenceFormPage />} />
      <Route path="/app/meetings/:meetingId" element={<div>Occurrence detail</div>} />
    </Routes>,
    { role: 'EDITOR', initialEntries: [entry] },
  );
}

describe('OccurrenceFormPage — create', () => {
  it('creates an occurrence and navigates to it', async () => {
    let sent: { meeting_id?: string; meeting_date?: string } = {};
    server.use(
      http.post(`${BASE}/meeting-occurrences`, async ({ request }) => {
        sent = (await request.json()) as typeof sent;
        return HttpResponse.json(makeOccurrence({ id: 'occ-new' }), { status: 201 });
      }),
    );
    const user = userEvent.setup();
    renderAt('/app/meetings/new');

    await user.selectOptions(await screen.findByLabelText('Meeting type'), 'mt-1');
    fireEvent.change(screen.getByLabelText('Meeting date'), { target: { value: '2026-08-01' } });
    await user.click(screen.getByRole('button', { name: /create occurrence/i }));

    expect(await screen.findByText('Occurrence detail')).toBeInTheDocument();
    expect(sent.meeting_id).toBe('mt-1');
    expect(sent.meeting_date).toBe('2026-08-01');
  });
});

describe('OccurrenceFormPage — edit', () => {
  it('populates fields, keeps the type read-only, and PATCHes only changes', async () => {
    let patched: Record<string, unknown> | null = null;
    server.use(
      http.patch(`${BASE}/meeting-occurrences/:id`, async ({ request, params }) => {
        patched = (await request.json()) as Record<string, unknown>;
        return HttpResponse.json(makeOccurrence({ id: String(params.id) }));
      }),
    );
    const user = userEvent.setup();
    renderAt('/app/meetings/occ-1/edit');

    // Type name is shown read-only (from the occurrence's meeting_id -> mt-1).
    expect(await screen.findByDisplayValue('Weekly Progress Meeting')).toBeInTheDocument();
    expect(screen.getByLabelText('Meeting date')).toHaveValue('2026-07-10');

    const agenda = screen.getByLabelText('Agenda');
    await user.clear(agenda);
    await user.type(agenda, 'Revised agenda');
    await user.click(screen.getByRole('button', { name: /save changes/i }));

    expect(await screen.findByText(/Meeting occurrence updated/i)).toBeInTheDocument();
    expect(patched).toEqual({ agenda: 'Revised agenda' });
  });
});
