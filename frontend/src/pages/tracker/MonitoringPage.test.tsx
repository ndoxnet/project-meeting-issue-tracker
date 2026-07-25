// Concept by MrHan (08974747477)
import { describe, expect, it } from 'vitest';
import { screen } from '@testing-library/react';
import { Route, Routes } from 'react-router-dom';
import { http, HttpResponse } from 'msw';
import { server } from '@/test/server';
import { renderWithProviders } from '@/test/utils';
import { MonitoringPage } from './MonitoringPage';

const BASE = '/api/v1';

function renderView(view: string) {
  return renderWithProviders(
    <Routes>
      <Route path="/app/dashboard" element={<div>Dashboard Home</div>} />
      <Route path="/app/monitoring/:view" element={<MonitoringPage />} />
    </Routes>,
    { initialEntries: [`/app/monitoring/${view}`] },
  );
}

describe('MonitoringPage', () => {
  it('renders the overdue list from the dedicated endpoint', async () => {
    renderView('overdue');
    expect(
      await screen.findByRole('heading', { name: /overdue issues/i }),
    ).toBeInTheDocument();
    expect(await screen.findByText(/Vendor commissioning attendance/i)).toBeInTheDocument();
  });

  it('shows an empty state when the view has no issues', async () => {
    server.use(http.get(`${BASE}/dashboard/stagnant`, () => HttpResponse.json([])));
    renderView('stagnant');
    expect(await screen.findByText(/Nothing here right now/i)).toBeInTheDocument();
  });

  it('redirects an unknown view to the dashboard', async () => {
    renderView('bogus');
    expect(await screen.findByText('Dashboard Home')).toBeInTheDocument();
  });
});
