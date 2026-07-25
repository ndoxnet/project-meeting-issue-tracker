// Concept by MrHan (08974747477)
import { describe, expect, it } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithProviders } from '@/test/utils';
import { TrackerLandingPage } from './TrackerLandingPage';

describe('TrackerLandingPage', () => {
  it('renders real dashboard counts and sections', async () => {
    renderWithProviders(<TrackerLandingPage />, { initialEntries: ['/app/dashboard'] });
    // Summary card labels + a value from the summary handler (overdue = 1).
    expect(await screen.findByText('Overdue')).toBeInTheDocument();
    expect(screen.getByText('Recently updated issues')).toBeInTheDocument();
    expect(screen.getByText('Recent meetings')).toBeInTheDocument();
    // Recently-updated issue loads.
    expect(await screen.findByText(/Vendor commissioning attendance/i)).toBeInTheDocument();
  });

  it('links overdue count to the filtered issues view', async () => {
    renderWithProviders(<TrackerLandingPage />, { initialEntries: ['/app/dashboard'] });
    const overdue = await screen.findByRole('link', { name: /overdue/i });
    expect(overdue).toHaveAttribute('href', '/app/issues?overdue=true');
  });
});
