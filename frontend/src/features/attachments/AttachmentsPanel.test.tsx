// Concept by MrHan (08974747477)
import { describe, expect, it, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { server } from '@/test/server';
import { renderWithProviders } from '@/test/utils';
import { ATTACHMENT_MAX_BYTES } from './config';
import { AttachmentsPanel } from './AttachmentsPanel';

const BASE = '/api/v1';

function pdf(name: string, size = 2048): File {
  const file = new File(['%PDF-1.4 body'], name, { type: 'application/pdf' });
  Object.defineProperty(file, 'size', { value: size });
  return file;
}

describe('AttachmentsPanel', () => {
  it('lists existing attachments', async () => {
    renderWithProviders(<AttachmentsPanel issueId="iss-1" archived={false} />);
    expect(await screen.findByText('evidence-report.pdf')).toBeInTheDocument();
  });

  it('shows an empty state when there are no attachments', async () => {
    server.use(http.get(`${BASE}/issues/:id/attachments`, () => HttpResponse.json([])));
    renderWithProviders(<AttachmentsPanel issueId="iss-1" archived={false} />);
    expect(await screen.findByText(/No attachments yet/i)).toBeInTheDocument();
  });

  it('hides upload and remove controls from viewers', async () => {
    renderWithProviders(<AttachmentsPanel issueId="iss-1" archived={false} />, { role: 'VIEWER' });
    expect(await screen.findByText('evidence-report.pdf')).toBeInTheDocument();
    expect(screen.queryByLabelText(/upload attachment/i)).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /remove evidence-report/i })).not.toBeInTheDocument();
    // Download stays available to everyone.
    expect(screen.getByRole('button', { name: /download/i })).toBeInTheDocument();
  });

  it('rejects an oversized file client-side without hitting the network', async () => {
    const user = userEvent.setup();
    renderWithProviders(<AttachmentsPanel issueId="iss-1" archived={false} />);
    await screen.findByText('evidence-report.pdf');

    await user.upload(screen.getByLabelText('File'), pdf('big.pdf', ATTACHMENT_MAX_BYTES + 1));
    await user.click(screen.getByRole('button', { name: /^upload$/i }));

    // Shown both inline and as a toast — the maximum size is surfaced.
    expect((await screen.findAllByText(/maximum is 10 MB/i)).length).toBeGreaterThan(0);
  });

  it('uploads a valid file and confirms success', async () => {
    const user = userEvent.setup();
    renderWithProviders(<AttachmentsPanel issueId="iss-1" archived={false} />);
    await screen.findByText('evidence-report.pdf');

    await user.upload(screen.getByLabelText('File'), pdf('ok.pdf'));
    await user.click(screen.getByRole('button', { name: /^upload$/i }));

    expect(await screen.findByText(/Attachment uploaded/i)).toBeInTheDocument();
  });

  it('lets an admin remove an attachment after confirmation', async () => {
    const user = userEvent.setup();
    renderWithProviders(<AttachmentsPanel issueId="iss-1" archived={false} />, { role: 'ADMIN' });
    await screen.findByText('evidence-report.pdf');

    await user.click(screen.getByRole('button', { name: /remove evidence-report/i }));
    await user.click(screen.getByRole('button', { name: /^remove$/i }));

    expect(await screen.findByText(/Attachment removed/i)).toBeInTheDocument();
  });

  it('downloads via a temporary object URL that is revoked', async () => {
    const user = userEvent.setup();
    const create = vi.spyOn(URL, 'createObjectURL');
    const revoke = vi.spyOn(URL, 'revokeObjectURL');
    renderWithProviders(<AttachmentsPanel issueId="iss-1" archived={false} />);
    await screen.findByText('evidence-report.pdf');

    await user.click(screen.getByRole('button', { name: /download/i }));

    await waitFor(() => expect(create).toHaveBeenCalled());
    expect(revoke).toHaveBeenCalled();
  });
});
