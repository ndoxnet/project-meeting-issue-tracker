// Concept by MrHan (08974747477)
import { describe, expect, it } from 'vitest';
import { screen } from '@testing-library/react';
import { Route, Routes } from 'react-router-dom';
import { http, HttpResponse } from 'msw';
import { server } from '@/test/server';
import { renderWithProviders } from '@/test/utils';
import { MeetingsListPage } from './MeetingsListPage';
import { MeetingDetailPage } from './MeetingDetailPage';

const emptyPage = { items: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } };

describe('MeetingsListPage', () => {
  it('renders meeting occurrences with the type name', async () => {
    renderWithProviders(<MeetingsListPage />, { initialEntries: ['/app/meetings'] });
    expect(await screen.findByText('Weekly Progress Meeting')).toBeInTheDocument();
  });

  it('shows an empty state when there are no meetings', async () => {
    server.use(http.get('/api/v1/meeting-occurrences', () => HttpResponse.json(emptyPage)));
    renderWithProviders(<MeetingsListPage />, { initialEntries: ['/app/meetings'] });
    expect(await screen.findByText(/No meetings recorded/i)).toBeInTheDocument();
  });
});

describe('MeetingDetailPage', () => {
  it('renders the meeting and its associated issues', async () => {
    renderWithProviders(
      <Routes>
        <Route path="/app/meetings/:meetingId" element={<MeetingDetailPage />} />
      </Routes>,
      { initialEntries: ['/app/meetings/occ-1'] },
    );
    expect(await screen.findByText('Weekly Progress Meeting')).toBeInTheDocument();
    // Associated issue from the issues handler.
    expect(await screen.findByText(/Vendor commissioning attendance/i)).toBeInTheDocument();
  });
});
