// Concept by MrHan (08974747477)
import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ToastProvider, useToast } from './ToastProvider';

function Trigger({ level, message }: { level: 'success' | 'error'; message: string }) {
  const toast = useToast();
  return (
    <button type="button" onClick={() => toast[level](message)}>
      fire
    </button>
  );
}

describe('ToastProvider', () => {
  it('shows a success toast in a polite status region', async () => {
    const user = userEvent.setup();
    render(
      <ToastProvider>
        <Trigger level="success" message="Saved!" />
      </ToastProvider>,
    );
    await user.click(screen.getByRole('button', { name: 'fire' }));
    const toast = await screen.findByRole('status');
    expect(toast).toHaveTextContent('Saved!');
  });

  it('shows an error toast as an assertive alert', async () => {
    const user = userEvent.setup();
    render(
      <ToastProvider>
        <Trigger level="error" message="It broke" />
      </ToastProvider>,
    );
    await user.click(screen.getByRole('button', { name: 'fire' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('It broke');
  });

  it('de-duplicates identical toasts fired in quick succession', async () => {
    const user = userEvent.setup();
    render(
      <ToastProvider>
        <Trigger level="success" message="Saved!" />
      </ToastProvider>,
    );
    const button = screen.getByRole('button', { name: 'fire' });
    await user.click(button);
    await user.click(button);
    expect(await screen.findByText('Saved!')).toBeInTheDocument();
    expect(screen.getAllByText('Saved!')).toHaveLength(1);
  });
});
