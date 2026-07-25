// Concept by MrHan (08974747477)
import { describe, expect, it } from 'vitest';
import { fireEvent, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { Route, Routes } from 'react-router-dom';
import { server } from '@/test/server';
import { renderWithProviders } from '@/test/utils';
import { makeIssueDetail } from '@/test/trackerHandlers';
import { IssueEditPage } from './IssueEditPage';

function renderEdit() {
  return renderWithProviders(
    <Routes>
      <Route path="/app/issues/:issueId/edit" element={<IssueEditPage />} />
      <Route path="/app/issues/:issueId" element={<div>Detail Page</div>} />
    </Routes>,
    { initialEntries: ['/app/issues/iss-1/edit'] },
  );
}

describe('IssueEditPage', () => {
  it('populates the form from the existing issue', async () => {
    renderEdit();
    expect(
      await screen.findByDisplayValue('Vendor commissioning attendance is pending'),
    ).toBeInTheDocument();
    expect(screen.getByDisplayValue('Budi')).toBeInTheDocument();
  });

  it('requires a change reason when the due date changes', async () => {
    const user = userEvent.setup();
    renderEdit();
    await screen.findByDisplayValue('Vendor commissioning attendance is pending');
    fireEvent.change(screen.getByLabelText(/due date/i), { target: { value: '2026-09-15' } });
    await user.click(screen.getByRole('button', { name: /save changes/i }));
    expect(await screen.findByText(/change reason is required/i)).toBeInTheDocument();
  });

  it('saves a changed title and navigates back to the issue', async () => {
    let patched: Record<string, unknown> | null = null;
    server.use(
      http.patch('/api/v1/issues/:id', async ({ request, params }) => {
        patched = (await request.json()) as Record<string, unknown>;
        return HttpResponse.json(makeIssueDetail({ id: String(params.id) }));
      }),
    );
    const user = userEvent.setup();
    renderEdit();
    const title = await screen.findByDisplayValue('Vendor commissioning attendance is pending');
    await user.clear(title);
    await user.type(title, 'Revised title');
    await user.click(screen.getByRole('button', { name: /save changes/i }));

    expect(await screen.findByText('Detail Page')).toBeInTheDocument();
    await waitFor(() => expect(patched).not.toBeNull());
    expect(patched).toEqual({ title: 'Revised title' }); // only the changed field is sent
  });
});
