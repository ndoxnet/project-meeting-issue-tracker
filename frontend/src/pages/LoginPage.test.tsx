// Concept by MrHan (08974747477)
import { describe, expect, it, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginPage } from './LoginPage';
import { renderWithRealAuth } from '@/test/utils';
import { getAccessToken } from '@/auth/tokenStore';

describe('LoginPage', () => {
  it('has accessible, labelled fields with autocomplete', () => {
    renderWithRealAuth(<LoginPage />);
    const username = screen.getByLabelText(/username or email/i);
    const password = screen.getByLabelText(/^password$/i);
    expect(username).toHaveAttribute('autocomplete', 'username');
    expect(password).toHaveAttribute('autocomplete', 'current-password');
  });

  it('validates required fields', async () => {
    const user = userEvent.setup();
    renderWithRealAuth(<LoginPage />);
    await user.click(screen.getByRole('button', { name: /sign in/i }));
    expect(await screen.findByText(/username or email is required/i)).toBeInTheDocument();
    expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    expect(getAccessToken()).toBeNull();
  });

  it('logs in with valid credentials and stores the token in memory', async () => {
    const user = userEvent.setup();
    renderWithRealAuth(<LoginPage />);
    await user.type(screen.getByLabelText(/username or email/i), 'editor1');
    await user.type(screen.getByLabelText(/^password$/i), 'correct-password');
    await user.click(screen.getByRole('button', { name: /sign in/i }));
    await waitFor(() => expect(getAccessToken()).toBe('test-token-EDITOR'));
  });

  it('shows a generic error on bad credentials and does not log them', async () => {
    const logSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
    const errSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    const user = userEvent.setup();
    renderWithRealAuth(<LoginPage />);
    await user.type(screen.getByLabelText(/username or email/i), 'editor1');
    await user.type(screen.getByLabelText(/^password$/i), 'wrong-password');
    await user.click(screen.getByRole('button', { name: /sign in/i }));
    expect(await screen.findByText(/invalid username or password/i)).toBeInTheDocument();
    expect(getAccessToken()).toBeNull();
    const logged = [...logSpy.mock.calls, ...errSpy.mock.calls].flat().join(' ');
    expect(logged).not.toContain('wrong-password');
    logSpy.mockRestore();
    errSpy.mockRestore();
  });

  it('toggles password visibility', async () => {
    const user = userEvent.setup();
    renderWithRealAuth(<LoginPage />);
    const password = screen.getByLabelText(/^password$/i);
    expect(password).toHaveAttribute('type', 'password');
    await user.click(screen.getByRole('button', { name: /show password/i }));
    expect(password).toHaveAttribute('type', 'text');
  });
});
