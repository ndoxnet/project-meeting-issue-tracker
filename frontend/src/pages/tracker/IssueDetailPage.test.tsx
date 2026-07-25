// Concept by MrHan (08974747477)
import { describe, expect, it } from 'vitest';
import { screen } from '@testing-library/react';
import { Route, Routes } from 'react-router-dom';
import { http, HttpResponse } from 'msw';
import { server } from '@/test/server';
import { renderWithProviders } from '@/test/utils';
import { IssueDetailPage } from './IssueDetailPage';

function renderDetail(id = 'iss-1', role: 'EDITOR' | 'VIEWER' = 'EDITOR') {
  return renderWithProviders(
    <Routes>
      <Route path="/app/issues/:issueId" element={<IssueDetailPage />} />
    </Routes>,
    { role, initialEntries: [`/app/issues/${id}`] },
  );
}

describe('IssueDetailPage', () => {
  it('renders issue detail and the follow-up timeline', async () => {
    renderDetail();
    expect(await screen.findByText(/Vendor commissioning attendance/i)).toBeInTheDocument();
    expect(screen.getByText('ISS-2026-0001')).toBeInTheDocument();
    // Timeline entry from the updates handler.
    expect(await screen.findByText(/Contractor mobilizing manpower/i)).toBeInTheDocument();
  });

  it('shows lifecycle actions for an editor', async () => {
    renderDetail('iss-1', 'EDITOR');
    expect(await screen.findByRole('button', { name: /add follow-up/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /edit/i })).toBeInTheDocument();
  });

  it('hides edit/actions for a viewer', async () => {
    renderDetail('iss-1', 'VIEWER');
    await screen.findByText(/Vendor commissioning/i);
    expect(screen.queryByRole('button', { name: /add follow-up/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /^edit$/i })).not.toBeInTheDocument();
  });

  it('shows an error when the issue is not found', async () => {
    server.use(
      http.get('/api/v1/issues/:id', () =>
        HttpResponse.json({ error: { code: 'ISSUE_NOT_FOUND', message: 'Issue not found' } }, { status: 404 }),
      ),
    );
    renderDetail('missing');
    expect(await screen.findByRole('alert')).toHaveTextContent(/not found/i);
  });
});
