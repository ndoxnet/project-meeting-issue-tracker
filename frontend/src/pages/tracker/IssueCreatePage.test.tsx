// Concept by MrHan (08974747477)
import { describe, expect, it } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { Route, Routes } from 'react-router-dom';
import { server } from '@/test/server';
import { renderWithProviders } from '@/test/utils';
import { makeIssueDetail } from '@/test/trackerHandlers';
import { IssueCreatePage } from './IssueCreatePage';

function renderCreate() {
  return renderWithProviders(
    <Routes>
      <Route path="/app/issues/new" element={<IssueCreatePage />} />
      <Route path="/app/issues/:id" element={<div>Detail Page</div>} />
    </Routes>,
    { initialEntries: ['/app/issues/new'] },
  );
}

describe('IssueCreatePage', () => {
  it('validates required fields', async () => {
    const user = userEvent.setup();
    renderCreate();
    await user.click(screen.getByRole('button', { name: /create issue/i }));
    expect(await screen.findByText(/title is required/i)).toBeInTheDocument();
    expect(screen.getByText(/description is required/i)).toBeInTheDocument();
  });

  it('submits the correct payload and navigates to the new issue', async () => {
    let body: Record<string, unknown> | null = null;
    server.use(
      http.post('/api/v1/issues', async ({ request }) => {
        body = (await request.json()) as Record<string, unknown>;
        return HttpResponse.json({ issue: makeIssueDetail({ id: 'iss-new' }), warnings: [] }, { status: 201 });
      }),
    );
    const user = userEvent.setup();
    renderCreate();
    // Wait for category options to load.
    await screen.findByRole('option', { name: 'Engineering' });

    await user.type(screen.getByLabelText(/^title/i), 'New commissioning issue');
    await user.type(screen.getByLabelText(/^description/i), 'Details here');
    await user.selectOptions(screen.getByLabelText(/^category/i), 'cat-Engineering');

    await user.click(screen.getByRole('button', { name: /create issue/i }));

    expect(await screen.findByText('Detail Page')).toBeInTheDocument();
    await waitFor(() => expect(body).not.toBeNull());
    expect(body).toMatchObject({
      title: 'New commissioning issue',
      description: 'Details here',
      category_id: 'cat-Engineering',
      confirm_possible_duplicate: false,
    });
  });
});
