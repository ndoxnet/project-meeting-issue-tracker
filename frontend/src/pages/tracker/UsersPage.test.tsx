// Concept by MrHan (08974747477)
import { describe, expect, it } from 'vitest';
import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { server } from '@/test/server';
import { renderWithProviders } from '@/test/utils';
import { makeUser } from '@/test/handlers';
import type { UserRole } from '@/api/types';
import { UsersPage } from './UsersPage';

const BASE = '/api/v1';

function renderUsers(role: UserRole = 'ADMIN') {
  return renderWithProviders(<UsersPage />, { role, initialEntries: ['/app/users'] });
}

async function rowOf(name: string): Promise<HTMLElement> {
  // Wait for the async list to render the record before locating its row.
  const row = (await screen.findByText(name)).closest('li');
  expect(row).not.toBeNull();
  return row as HTMLElement;
}

describe('UsersPage', () => {
  it('lists users with role and status', async () => {
    renderUsers();
    expect(await screen.findByText('ADMIN User')).toBeInTheDocument();
    expect(screen.getByText('EDITOR User')).toBeInTheDocument();
    expect(screen.getAllByText('Active').length).toBeGreaterThan(0);
  });

  it('creates a user and sends the full payload', async () => {
    let body: Record<string, unknown> | null = null;
    server.use(
      http.post(`${BASE}/users`, async ({ request }) => {
        body = (await request.json()) as Record<string, unknown>;
        return HttpResponse.json(makeUser('EDITOR', 'newperson'), { status: 201 });
      }),
    );
    const user = userEvent.setup();
    renderUsers();
    await user.click(screen.getByRole('button', { name: /new user/i }));
    await user.type(screen.getByLabelText(/username/i), 'newperson');
    await user.type(screen.getByLabelText(/full name/i), 'New Person');
    await user.type(screen.getByLabelText(/email/i), 'new@example.com');
    await user.selectOptions(screen.getByLabelText(/role/i), 'EDITOR');
    await user.type(screen.getByLabelText(/initial password/i), 'BrandNewPass12');
    await user.click(screen.getByRole('button', { name: /create user/i }));

    expect(await screen.findByText(/User created/i)).toBeInTheDocument();
    expect(body).toMatchObject({
      username: 'newperson',
      email: 'new@example.com',
      full_name: 'New Person',
      role: 'EDITOR',
      password: 'BrandNewPass12',
    });
  });

  it('keeps create disabled until the password meets the minimum length', async () => {
    const user = userEvent.setup();
    renderUsers();
    await user.click(screen.getByRole('button', { name: /new user/i }));
    await user.type(screen.getByLabelText(/username/i), 'newperson');
    await user.type(screen.getByLabelText(/full name/i), 'New Person');
    await user.type(screen.getByLabelText(/email/i), 'new@example.com');
    await user.type(screen.getByLabelText(/initial password/i), 'short');
    expect(screen.getByRole('button', { name: /create user/i })).toBeDisabled();
  });

  it('surfaces a conflict error inline in the create form', async () => {
    server.use(
      http.post(`${BASE}/users`, () =>
        HttpResponse.json({ error: { code: 'CONFLICT', message: 'Username already exists' } }, { status: 409 }),
      ),
    );
    const user = userEvent.setup();
    renderUsers();
    await user.click(screen.getByRole('button', { name: /new user/i }));
    await user.type(screen.getByLabelText(/username/i), 'admin1');
    await user.type(screen.getByLabelText(/full name/i), 'Dup');
    await user.type(screen.getByLabelText(/email/i), 'dup@example.com');
    await user.type(screen.getByLabelText(/initial password/i), 'ValidPass1234');
    await user.click(screen.getByRole('button', { name: /create user/i }));

    const dialog = await screen.findByRole('dialog');
    expect(within(dialog).getByText(/Username already exists/i)).toBeInTheDocument();
  });

  it('edits a user and PATCHes only changed fields', async () => {
    let body: Record<string, unknown> | null = null;
    server.use(
      http.patch(`${BASE}/users/:id`, async ({ request, params }) => {
        body = (await request.json()) as Record<string, unknown>;
        return HttpResponse.json({ ...makeUser('EDITOR', 'editor1'), id: String(params.id) });
      }),
    );
    const user = userEvent.setup();
    renderUsers();
    await user.click(within(await rowOf('EDITOR User')).getByRole('button', { name: 'Edit' }));
    const fullName = screen.getByLabelText(/full name/i);
    await user.clear(fullName);
    await user.type(fullName, 'Edited Editor');
    await user.click(screen.getByRole('button', { name: /save changes/i }));

    expect(await screen.findByText(/User updated/i)).toBeInTheDocument();
    expect(body).toEqual({ full_name: 'Edited Editor' });
  });

  it('changes a user role via edit', async () => {
    let body: Record<string, unknown> | null = null;
    server.use(
      http.patch(`${BASE}/users/:id`, async ({ request, params }) => {
        body = (await request.json()) as Record<string, unknown>;
        return HttpResponse.json({ ...makeUser('ADMIN', 'editor1'), id: String(params.id) });
      }),
    );
    const user = userEvent.setup();
    renderUsers();
    await user.click(within(await rowOf('EDITOR User')).getByRole('button', { name: 'Edit' }));
    await user.selectOptions(screen.getByLabelText(/role/i), 'ADMIN');
    await user.click(screen.getByRole('button', { name: /save changes/i }));

    expect(await screen.findByText(/User updated/i)).toBeInTheDocument();
    expect(body).toEqual({ role: 'ADMIN' });
  });

  it('prevents changing your own role in the UI', async () => {
    const user = userEvent.setup();
    renderUsers(); // current user is ADMIN → matches the admin row (self)
    await user.click(within(await rowOf('ADMIN User')).getByRole('button', { name: 'Edit' }));
    expect(screen.getByLabelText(/role/i)).toBeDisabled();
    expect(screen.getByText(/cannot change your own role/i)).toBeInTheDocument();
  });

  it('disables deactivating your own account but allows others', async () => {
    renderUsers();
    await screen.findByText('ADMIN User');
    expect(within(await rowOf('ADMIN User')).getByRole('button', { name: 'Deactivate' })).toBeDisabled();
    expect(within(await rowOf('EDITOR User')).getByRole('button', { name: 'Deactivate' })).toBeEnabled();
  });

  it('surfaces the last-admin deactivation error inline in the confirm dialog', async () => {
    server.use(
      http.post(`${BASE}/users/:id/deactivate`, () =>
        HttpResponse.json(
          { error: { code: 'VALIDATION_ERROR', message: 'Cannot deactivate the only active admin' } },
          { status: 422 },
        ),
      ),
    );
    const user = userEvent.setup();
    renderUsers();
    await user.click(within(await rowOf('EDITOR User')).getByRole('button', { name: 'Deactivate' }));
    const dialog = await screen.findByRole('dialog');
    await user.click(within(dialog).getByRole('button', { name: 'Deactivate' }));
    expect(await within(dialog).findByText(/only active admin/i)).toBeInTheDocument();
  });

  it('resets a password, shows the session-validity note, and sends the payload', async () => {
    let body: Record<string, unknown> | null = null;
    server.use(
      http.post(`${BASE}/users/:id/reset-password`, async ({ request }) => {
        body = (await request.json()) as Record<string, unknown>;
        return HttpResponse.json({ message: 'Password has been reset.' });
      }),
    );
    const user = userEvent.setup();
    renderUsers();
    await user.click(within(await rowOf('EDITOR User')).getByRole('button', { name: /reset password/i }));
    const dialog = await screen.findByRole('dialog');
    expect(within(dialog).getByText(/sessions remain valid until/i)).toBeInTheDocument();
    await user.type(within(dialog).getByLabelText(/new password/i), 'FreshPass12345');
    await user.click(within(dialog).getByRole('button', { name: /reset password/i }));

    expect(await screen.findByText(/Password reset for editor1/i)).toBeInTheDocument();
    expect(body).toEqual({ new_password: 'FreshPass12345' });
  });
});
