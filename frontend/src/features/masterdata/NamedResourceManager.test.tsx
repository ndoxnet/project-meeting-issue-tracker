// Concept by MrHan (08974747477)
import { describe, expect, it } from 'vitest';
import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { server } from '@/test/server';
import { renderWithProviders } from '@/test/utils';
import { NamedResourceManager } from './NamedResourceManager';

const BASE = '/api/v1';

function render() {
  return renderWithProviders(
    <NamedResourceManager kind="categories" singular="Category" />,
    { role: 'ADMIN' },
  );
}

describe('NamedResourceManager', () => {
  it('lists records with their active status', async () => {
    render();
    expect(await screen.findByText('Engineering')).toBeInTheDocument();
    expect(screen.getByText('Procurement')).toBeInTheDocument();
    expect(screen.getAllByText('Active').length).toBeGreaterThan(0);
  });

  it('creates a record and confirms success', async () => {
    let sentName: string | null = null;
    server.use(
      http.post(`${BASE}/categories`, async ({ request }) => {
        sentName = ((await request.json()) as { name: string }).name;
        return HttpResponse.json({ id: 'x', name: sentName, description: null, is_active: true, created_at: '', updated_at: '' }, { status: 201 });
      }),
    );
    const user = userEvent.setup();
    render();
    await screen.findByText('Engineering');

    await user.click(screen.getByRole('button', { name: /new category/i }));
    await user.type(screen.getByLabelText('Name'), 'Safety');
    await user.click(screen.getByRole('button', { name: /create category/i }));

    expect(await screen.findByText(/Category created/i)).toBeInTheDocument();
    expect(sentName).toBe('Safety');
  });

  it('deactivates with an explicit not-a-deletion confirmation', async () => {
    const user = userEvent.setup();
    render();
    await screen.findByText('Engineering');

    await user.click(screen.getAllByRole('button', { name: 'Deactivate' })[0]);
    const dialog = await screen.findByRole('dialog');
    expect(within(dialog).getByText(/not a deletion/i)).toBeInTheDocument();
    await user.click(within(dialog).getByRole('button', { name: 'Deactivate' }));

    expect(await screen.findByText(/Category deactivated/i)).toBeInTheDocument();
  });

  it('sends the active/inactive filter to the API', async () => {
    let seen: string | null = null;
    server.use(
      http.get(`${BASE}/categories`, ({ request }) => {
        seen = new URL(request.url).searchParams.get('is_active');
        return HttpResponse.json({ items: [], meta: { page: 1, page_size: 50, total: 0, pages: 0 } });
      }),
    );
    const user = userEvent.setup();
    render();
    await user.selectOptions(screen.getByLabelText(/filter category by status/i), 'inactive');
    await waitFor(() => expect(seen).toBe('false'));
  });

  it('surfaces a validation error inline in the create form', async () => {
    server.use(
      http.post(`${BASE}/categories`, () =>
        HttpResponse.json({ error: { code: 'CONFLICT', message: 'Name already exists' } }, { status: 409 }),
      ),
    );
    const user = userEvent.setup();
    render();
    await screen.findByText('Engineering');

    await user.click(screen.getByRole('button', { name: /new category/i }));
    await user.type(screen.getByLabelText('Name'), 'Engineering');
    await user.click(screen.getByRole('button', { name: /create category/i }));

    const dialog = await screen.findByRole('dialog');
    expect(within(dialog).getByText(/Name already exists/i)).toBeInTheDocument();
  });
});
