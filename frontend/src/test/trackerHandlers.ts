// Concept by MrHan (08974747477)
// MSW handlers + fixtures for meetings/issues/dashboard/master-data (frozen v1).
import { http, HttpResponse } from 'msw';
import { makeUser } from './handlers';
import type {
  AppSettingResponse,
  AttachmentResponse,
  CountByLabel,
  DashboardSummary,
  IssueCreateResponse,
  IssueDetailResponse,
  IssueListItem,
  IssueUpdateResponse,
  MeetingOccurrence,
  MonthlyTrendPoint,
  NamedResponse,
  Page,
  UserResponse,
  VoidResponse,
} from '@/api/types';

const BASE = '/api/v1';

export function makeNamed(name: string, id = `cat-${name}`): NamedResponse {
  return {
    id,
    name,
    description: null,
    is_active: true,
    created_at: '2026-07-01T00:00:00Z',
    updated_at: '2026-07-01T00:00:00Z',
  };
}

export function makeOccurrence(over: Partial<MeetingOccurrence> = {}): MeetingOccurrence {
  return {
    id: 'occ-1',
    meeting_id: 'mt-1',
    meeting_date: '2026-07-10',
    meeting_number: '#14',
    reference_number: 'MoM-14',
    agenda: 'Weekly progress review',
    minutes_link: null,
    notes: null,
    created_by: 'user-1',
    created_at: '2026-07-10T00:00:00Z',
    updated_at: '2026-07-10T00:00:00Z',
    ...over,
  };
}

export function makeIssueListItem(over: Partial<IssueListItem> = {}): IssueListItem {
  return {
    id: 'iss-1',
    issue_code: 'ISS-2026-0001',
    title: 'Vendor commissioning attendance is pending',
    category_id: 'cat-Engineering',
    category_name: 'Engineering',
    responsible_party_id: null,
    responsible_party_name: null,
    priority: 'HIGH',
    status: 'OPEN',
    raised_date: '2026-07-10',
    pic_name: 'Budi',
    pic_user_id: null,
    due_date: '2026-08-01',
    days_open: 5,
    last_update_at: null,
    days_since_last_update: 5,
    next_action: 'Vendor to confirm',
    is_overdue: false,
    is_archived: false,
    ...over,
  };
}

export function makeIssueDetail(over: Partial<IssueDetailResponse> = {}): IssueDetailResponse {
  return {
    id: 'iss-1',
    issue_code: 'ISS-2026-0001',
    title: 'Vendor commissioning attendance is pending',
    description: 'Vendor engineer not yet mobilized.',
    category_id: 'cat-Engineering',
    category_name: 'Engineering',
    responsible_party_id: null,
    responsible_party_name: null,
    priority: 'HIGH',
    status: 'OPEN',
    raised_date: '2026-07-10',
    raised_in_meeting_occurrence_id: 'occ-1',
    pic_name: 'Budi',
    pic_user_id: null,
    due_date: '2026-08-01',
    next_action: 'Vendor to confirm',
    last_update_summary: null,
    last_update_at: null,
    closed_date: null,
    closure_note: null,
    reopened_at: null,
    archived_at: null,
    days_open: 5,
    days_since_last_update: 5,
    is_overdue: false,
    created_by: 'user-1',
    created_at: '2026-07-10T00:00:00Z',
    updated_by: 'user-1',
    updated_at: '2026-07-10T00:00:00Z',
    ...over,
  } as IssueDetailResponse;
}

export function makeIssueUpdate(over: Partial<IssueUpdateResponse> = {}): IssueUpdateResponse {
  return {
    id: 'upd-1',
    issue_id: 'iss-1',
    update_date: '2026-07-12',
    meeting_occurrence_id: null,
    update_note: 'Contractor mobilizing manpower.',
    decision: null,
    next_action: null,
    action_owner: null,
    target_date: null,
    progress_percentage: null,
    status_before: null,
    status_after: null,
    due_date_before: null,
    due_date_after: null,
    pic_before: null,
    pic_after: null,
    created_by: 'user-1',
    created_at: '2026-07-12T00:00:00Z',
    voided_at: null,
    voided_by: null,
    void_reason: null,
    ...over,
  };
}

export function makeAttachment(over: Partial<AttachmentResponse> = {}): AttachmentResponse {
  return {
    id: 'att-1',
    issue_id: 'iss-1',
    issue_update_id: null,
    original_filename: 'evidence-report.pdf',
    stored_filename: 'stored-abc123.pdf',
    mime_type: 'application/pdf',
    size_bytes: 20480,
    checksum_sha256: 'abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789',
    description: 'Vendor confirmation letter',
    uploaded_by: 'user-1',
    uploaded_at: '2026-07-13T02:00:00Z',
    removed_at: null,
    ...over,
  } as AttachmentResponse;
}

function page<T>(items: T[]): Page<T> {
  return { items, meta: { page: 1, page_size: 20, total: items.length, pages: 1 } };
}

const byCategory: CountByLabel[] = [
  { label: 'Engineering', count: 3 },
  { label: 'Procurement', count: 1 },
];
const byResponsibleParty: CountByLabel[] = [{ label: 'Main Contractor', count: 2 }];
const trend: MonthlyTrendPoint[] = [
  { month: '2026-06', opened: 4, closed: 2 },
  { month: '2026-07', opened: 5, closed: 3 },
];

const appSettings: AppSettingResponse[] = [
  {
    key: 'stagnant_days',
    value: 14,
    description: 'Days without an update before an issue is stagnant',
    updated_at: '2026-07-20T00:00:00Z',
  },
  {
    key: 'attachment_max_mb',
    value: 10,
    description: null,
    updated_at: '2026-07-20T00:00:00Z',
  },
  {
    key: 'attachment_allowed_types',
    value: ['application/pdf', 'image/jpeg', 'image/png'],
    description: null,
    updated_at: '2026-07-20T00:00:00Z',
  },
];

const summary: DashboardSummary = {
  open_count: 3,
  in_progress_count: 2,
  pending_count: 1,
  reopened_count: 0,
  overdue_count: 1,
  stagnant_count: 0,
  due_this_week_count: 2,
  closed_this_month_count: 4,
  total_active_count: 6,
};

export const trackerHandlers = [
  http.get(`${BASE}/dashboard/summary`, () => HttpResponse.json(summary)),
  http.get(`${BASE}/dashboard/recently-updated`, () =>
    HttpResponse.json([makeIssueListItem()]),
  ),
  http.get(`${BASE}/categories`, () =>
    HttpResponse.json(page([makeNamed('Engineering'), makeNamed('Procurement')])),
  ),
  http.get(`${BASE}/responsible-parties`, () =>
    HttpResponse.json(page([makeNamed('Main Contractor', 'rp-1')])),
  ),
  http.get(`${BASE}/meetings`, () =>
    HttpResponse.json(page([makeNamed('Weekly Progress Meeting', 'mt-1')])),
  ),
  http.get(`${BASE}/meeting-occurrences`, () => HttpResponse.json(page([makeOccurrence()]))),
  http.get(`${BASE}/meeting-occurrences/:id`, ({ params }) =>
    HttpResponse.json(makeOccurrence({ id: String(params.id) })),
  ),
  http.get(`${BASE}/issues`, () => HttpResponse.json(page([makeIssueListItem()]))),
  http.get(`${BASE}/issues/:id`, ({ params }) =>
    HttpResponse.json(makeIssueDetail({ id: String(params.id) })),
  ),
  http.get(`${BASE}/issues/:id/updates`, () => HttpResponse.json([makeIssueUpdate()])),
  http.post(`${BASE}/issues`, async () => {
    const res: IssueCreateResponse = { issue: makeIssueDetail({ id: 'iss-new' }), warnings: [] };
    return HttpResponse.json(res, { status: 201 });
  }),
  http.patch(`${BASE}/issues/:id`, ({ params }) =>
    HttpResponse.json(makeIssueDetail({ id: String(params.id), title: 'Updated title' })),
  ),
  http.post(`${BASE}/issues/:id/status`, ({ params }) =>
    HttpResponse.json(makeIssueDetail({ id: String(params.id), status: 'IN_PROGRESS' })),
  ),
  http.post(`${BASE}/issues/:id/close`, ({ params }) =>
    HttpResponse.json(makeIssueDetail({ id: String(params.id), status: 'CLOSED' })),
  ),
  http.post(`${BASE}/issues/:id/reopen`, ({ params }) =>
    HttpResponse.json(makeIssueDetail({ id: String(params.id), status: 'REOPENED' })),
  ),
  http.post(`${BASE}/issues/:id/updates`, () => HttpResponse.json(makeIssueUpdate(), { status: 201 })),

  // ---- attachments ----
  http.get(`${BASE}/issues/:id/attachments`, () => HttpResponse.json([makeAttachment()])),
  http.post(`${BASE}/issues/:id/attachments`, () =>
    HttpResponse.json(makeAttachment({ id: 'att-new' }), { status: 201 }),
  ),
  http.get(`${BASE}/issues/:id/attachments/:aid/download`, () =>
    new HttpResponse(new Blob(['%PDF-1.4 fake'], { type: 'application/pdf' }), {
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'attachment; filename="evidence-report.pdf"',
      },
    }),
  ),
  http.post(`${BASE}/issues/:id/attachments/:aid/remove`, () =>
    HttpResponse.json({ message: 'Attachment removed.' }),
  ),

  // ---- reports ----
  http.get(`${BASE}/reports/issues.csv`, () =>
    new HttpResponse('issue_code,title\nISS-2026-0001,Vendor commissioning attendance\n', {
      headers: {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename="issues-2026.csv"',
      },
    }),
  ),

  // ---- monitoring lists ----
  http.get(`${BASE}/dashboard/overdue`, () =>
    HttpResponse.json([makeIssueListItem({ is_overdue: true })]),
  ),
  http.get(`${BASE}/dashboard/stagnant`, () => HttpResponse.json([makeIssueListItem()])),
  http.get(`${BASE}/dashboard/due-this-week`, () => HttpResponse.json([makeIssueListItem()])),

  // ---- distributions & trend ----
  http.get(`${BASE}/dashboard/by-category`, () => HttpResponse.json(byCategory)),
  http.get(`${BASE}/dashboard/by-responsible-party`, () => HttpResponse.json(byResponsibleParty)),
  http.get(`${BASE}/dashboard/opened-vs-closed`, () => HttpResponse.json(trend)),

  // ---- master-data mutations (categories / responsible-parties / meetings) ----
  ...['/categories', '/responsible-parties', '/meetings'].flatMap((p) => [
    http.post(`${BASE}${p}`, async ({ request }) => {
      const body = (await request.json()) as { name?: string };
      return HttpResponse.json(makeNamed(body.name ?? 'New', 'named-new'), { status: 201 });
    }),
    http.patch(`${BASE}${p}/:id`, async ({ request, params }) => {
      const body = (await request.json()) as { name?: string };
      return HttpResponse.json(makeNamed(body.name ?? 'Updated', String(params.id)));
    }),
    http.post(`${BASE}${p}/:id/activate`, ({ params }) =>
      HttpResponse.json(makeNamed('Item', String(params.id))),
    ),
    http.post(`${BASE}${p}/:id/deactivate`, ({ params }) =>
      HttpResponse.json({ ...makeNamed('Item', String(params.id)), is_active: false }),
    ),
  ]),

  // ---- meeting-occurrence authoring ----
  http.post(`${BASE}/meeting-occurrences`, async ({ request }) => {
    const body = (await request.json()) as { meeting_id: string; meeting_date: string };
    return HttpResponse.json(
      makeOccurrence({ id: 'occ-new', meeting_id: body.meeting_id, meeting_date: body.meeting_date }),
      { status: 201 },
    );
  }),
  http.patch(`${BASE}/meeting-occurrences/:id`, ({ params }) =>
    HttpResponse.json(makeOccurrence({ id: String(params.id) })),
  ),

  // ---- user administration ----
  http.get(`${BASE}/users`, () =>
    HttpResponse.json(page<UserResponse>([makeUser('ADMIN', 'admin1'), makeUser('EDITOR', 'editor1')])),
  ),
  http.post(`${BASE}/users`, async ({ request }) => {
    const body = (await request.json()) as { username?: string };
    return HttpResponse.json(makeUser('EDITOR', body.username ?? 'newuser'), { status: 201 });
  }),
  http.patch(`${BASE}/users/:id`, async ({ params }) =>
    HttpResponse.json({ ...makeUser('EDITOR', 'editor1'), id: String(params.id) }),
  ),
  http.post(`${BASE}/users/:id/activate`, ({ params }) =>
    HttpResponse.json({ ...makeUser('EDITOR', 'editor1'), id: String(params.id), is_active: true }),
  ),
  http.post(`${BASE}/users/:id/deactivate`, ({ params }) =>
    HttpResponse.json({ ...makeUser('EDITOR', 'editor1'), id: String(params.id), is_active: false }),
  ),
  http.post(`${BASE}/users/:id/reset-password`, () =>
    HttpResponse.json({ message: 'Password has been reset.' }),
  ),

  // ---- app settings (read-only) ----
  http.get(`${BASE}/settings`, () => HttpResponse.json(appSettings)),

  // ---- void follow-up update ----
  http.post(`${BASE}/issues/:id/updates/:uid/void`, async ({ request, params }) => {
    const body = (await request.json()) as { void_reason: string };
    const res: VoidResponse = {
      update: makeIssueUpdate({
        id: String(params.uid),
        voided_at: '2026-07-20T00:00:00Z',
        voided_by: 'user-1',
        void_reason: body.void_reason,
      }),
      warnings: [],
    };
    return HttpResponse.json(res);
  }),
];
