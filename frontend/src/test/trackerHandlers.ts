// Concept by MrHan (08974747477)
// MSW handlers + fixtures for meetings/issues/dashboard/master-data (frozen v1).
import { http, HttpResponse } from 'msw';
import type {
  DashboardSummary,
  IssueCreateResponse,
  IssueDetailResponse,
  IssueListItem,
  IssueUpdateResponse,
  MeetingOccurrence,
  NamedResponse,
  Page,
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

function page<T>(items: T[]): Page<T> {
  return { items, meta: { page: 1, page_size: 20, total: items.length, pages: 1 } };
}

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
];
