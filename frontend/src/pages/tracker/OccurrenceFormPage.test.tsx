// Concept by MrHan (08974747477)
import { describe, expect, it } from 'vitest';
import { fireEvent, screen, waitFor } from '@testing-library/react';
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

    // Wait for the async meeting-types query to populate the <option>s before
    // selecting — otherwise only the placeholder option exists.
    const meetingTypeSelect = await screen.findByLabelText(/meeting type/i);
    await screen.findByRole('option', { name: /weekly progress meeting/i });
    await user.selectOptions(meetingTypeSelect, 'mt-1');
    expect(meetingTypeSelect).toHaveValue('mt-1');

    fireEvent.change(screen.getByLabelText(/meeting date/i), { target: { value: '2026-08-01' } });
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

    // Wait for the form to populate (occurrence loaded), then assert each control
    // by its label + value — never by display value (avoids the disabled/read-only
    // matching gap and ambiguity).
    expect(await screen.findByLabelText(/meeting date/i)).toHaveValue('2026-07-10');

    // Meeting type resolves from a separate query and is shown read-only/disabled.
    const meetingType = screen.getByLabelText(/meeting type/i);
    await waitFor(() => expect(meetingType).toHaveValue('Weekly Progress Meeting'));
    expect(meetingType).toBeDisabled();

    expect(screen.getByLabelText(/meeting number/i)).toHaveValue('#14');
    expect(screen.getByLabelText(/reference number/i)).toHaveValue('MoM-14');
    expect(screen.getByLabelText(/agenda/i)).toHaveValue('Weekly progress review');

    // Change one supported field; the PATCH must contain ONLY that field.
    await user.clear(screen.getByLabelText(/reference number/i));
    await user.type(screen.getByLabelText(/reference number/i), 'MoM-14 Revised');
    await user.click(screen.getByRole('button', { name: /save changes/i }));

    expect(await screen.findByText(/Meeting occurrence updated/i)).toBeInTheDocument();
    expect(patched).toEqual({ reference_number: 'MoM-14 Revised' });
  });
});
