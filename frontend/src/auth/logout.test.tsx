// Concept by MrHan (08974747477)
import { describe, expect, it } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { server } from '@/test/server';
import { useAuth } from './useAuth';
import { getAccessToken } from './tokenStore';
import { renderWithRealAuth } from '@/test/utils';

function Harness() {
  const { status, user, login, logout } = useAuth();
  return (
    <div>
      <div data-testid="status">{status}</div>
      <div data-testid="user">{user?.username ?? 'none'}</div>
      <button onClick={() => login({ username: 'editor1', password: 'correct-password' })}>
        do-login
      </button>
      <button onClick={() => logout()}>do-logout</button>
    </div>
  );
}

async function login(user: ReturnType<typeof userEvent.setup>) {
  await user.click(screen.getByText('do-login'));
  await waitFor(() => expect(screen.getByTestId('status')).toHaveTextContent('authenticated'));
}

describe('logout', () => {
  it('clears token, user, and query cache', async () => {
    const user = userEvent.setup();
    const { queryClient } = renderWithRealAuth(<Harness />);
    await login(user);
    queryClient.setQueryData(['sensitive'], { secret: 'data' });
    expect(getAccessToken()).toBe('test-token-EDITOR');

    await user.click(screen.getByText('do-logout'));
    await waitFor(() => expect(screen.getByTestId('status')).toHaveTextContent('unauthenticated'));
    expect(getAccessToken()).toBeNull();
    expect(screen.getByTestId('user')).toHaveTextContent('none');
    expect(queryClient.getQueryData(['sensitive'])).toBeUndefined();
  });

  it('clears locally even if the backend logout fails', async () => {
    const user = userEvent.setup();
    renderWithRealAuth(<Harness />);
    await login(user);
    server.use(
      http.post('/api/v1/auth/logout', () => new HttpResponse(null, { status: 500 })),
    );
    await user.click(screen.getByText('do-logout'));
    await waitFor(() => expect(screen.getByTestId('status')).toHaveTextContent('unauthenticated'));
    expect(getAccessToken()).toBeNull();
  });
});
