// Concept by MrHan (08974747477)
import { describe, expect, it } from 'vitest';
import { screen, within } from '@testing-library/react';
import { renderWithProviders } from '@/test/utils';
import { SettingsPage } from './SettingsPage';

describe('SettingsPage', () => {
  it('renders settings read-only with a reference banner and no edit controls', async () => {
    renderWithProviders(<SettingsPage />, { role: 'ADMIN', initialEntries: ['/app/settings'] });

    expect(await screen.findByText('stagnant_days')).toBeInTheDocument();
    expect(screen.getByText('14')).toBeInTheDocument();

    const note = screen.getByRole('note');
    expect(within(note).getByText(/read-only/i)).toBeInTheDocument();
    expect(within(note).getByText(/environment/i)).toBeInTheDocument();

    // Read-only: no editable fields or save controls.
    expect(screen.queryByRole('textbox')).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /save/i })).not.toBeInTheDocument();
  });
});
