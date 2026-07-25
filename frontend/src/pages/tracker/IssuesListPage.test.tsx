// Concept by MrHan (08974747477)
import { describe, expect, it } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { server } from '@/test/server';
import { renderWithProviders } from '@/test/utils';
import { makeIssueListItem } from '@/test/trackerHandlers';
import { IssuesListPage } from './IssuesListPage';

const emptyPage = { items: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } };

describe('IssuesListPage', () => {
  it('renders issues on success', async () => {
    renderWithProviders(<IssuesListPage />, { initialEntries: ['/app/issues'] });
    expect(await screen.findByText(/Vendor commissioning attendance/i)).toBeInTheDocument();
    expect(screen.getByText('ISS-2026-0001')).toBeInTheDocument();
  });

  it('shows an empty state when there are no issues', async () => {
    server.use(http.get('/api/v1/issues', () => HttpResponse.json(emptyPage)));
    renderWithProviders(<IssuesListPage />, { initialEntries: ['/app/issues'] });
    expect(await screen.findByText(/No issues match your filters/i)).toBeInTheDocument();
  });

  it('shows an error state on API failure', async () => {
    server.use(
      http.get('/api/v1/issues', () =>
        HttpResponse.json({ error: { code: 'INTERNAL_ERROR', message: 'boom' } }, { status: 500 }),
      ),
    );
    renderWithProviders(<IssuesListPage />, { initialEntries: ['/app/issues'] });
    expect(await screen.findByRole('alert')).toBeInTheDocument();
  });

  it('sends the status filter to the API', async () => {
    let seenStatus: string | null = null;
    server.use(
      http.get('/api/v1/issues', ({ request }) => {
        seenStatus = new URL(request.url).searchParams.get('status');
        return HttpResponse.json({ items: [makeIssueListItem()], meta: emptyPage.meta });
      }),
    );
    const user = userEvent.setup();
    renderWithProviders(<IssuesListPage />, { initialEntries: ['/app/issues'] });
    await screen.findByText(/Vendor commissioning/i);
    await user.selectOptions(screen.getByLabelText(/filter by status/i), 'PENDING');
    await waitFor(() => expect(seenStatus).toBe('PENDING'));
  });

  it('shows the New Issue action for an editor', async () => {
    renderWithProviders(<IssuesListPage />, { role: 'EDITOR', initialEntries: ['/app/issues'] });
    expect(await screen.findByRole('link', { name: /new issue/i })).toBeInTheDocument();
  });

  it('hides the New Issue action for a viewer', async () => {
    renderWithProviders(<IssuesListPage />, { role: 'VIEWER', initialEntries: ['/app/issues'] });
    await screen.findByText(/Vendor commissioning/i);
    expect(screen.queryByRole('link', { name: /new issue/i })).not.toBeInTheDocument();
  });
});
