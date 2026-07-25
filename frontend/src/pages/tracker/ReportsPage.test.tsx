// Concept by MrHan (08974747477)
import { describe, expect, it } from 'vitest';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { server } from '@/test/server';
import { renderWithProviders } from '@/test/utils';
import { ReportsPage } from './ReportsPage';

const BASE = '/api/v1';

describe('ReportsPage', () => {
  it('exports the register to CSV and confirms the download', async () => {
    const user = userEvent.setup();
    let requested: URL | null = null;
    server.use(
      http.get(`${BASE}/reports/issues.csv`, ({ request }) => {
        requested = new URL(request.url);
        return new HttpResponse('issue_code\nISS-2026-0001\n', {
          headers: {
            'Content-Type': 'text/csv',
            'Content-Disposition': 'attachment; filename="issues.csv"',
          },
        });
      }),
    );

    renderWithProviders(<ReportsPage />, { initialEntries: ['/app/reports'] });
    await user.click(screen.getByLabelText(/overdue issues only/i));
    await user.click(screen.getByRole('button', { name: /export issues to csv/i }));

    expect(await screen.findByText(/CSV downloaded/i)).toBeInTheDocument();
    expect(requested).not.toBeNull();
    // The active filter is forwarded; pagination is never sent.
    expect(requested!.searchParams.get('overdue')).toBe('true');
    expect(requested!.searchParams.has('page')).toBe(false);
  });

  it('surfaces an export-limit error as a toast', async () => {
    const user = userEvent.setup();
    server.use(
      http.get(`${BASE}/reports/issues.csv`, () =>
        HttpResponse.json(
          {
            error: {
              code: 'EXPORT_LIMIT_EXCEEDED',
              message: 'Export exceeds the maximum of 10000 rows; narrow the filters',
            },
          },
          { status: 409 },
        ),
      ),
    );

    renderWithProviders(<ReportsPage />, { initialEntries: ['/app/reports'] });
    await user.click(screen.getByRole('button', { name: /export issues to csv/i }));

    expect(await screen.findByText(/narrow the filters/i)).toBeInTheDocument();
  });
});
