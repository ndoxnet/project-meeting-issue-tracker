// Concept by MrHan (08974747477)
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { ProtectedRoute } from '@/auth/ProtectedRoute';
import { RoleRoute } from '@/auth/RoleRoute';
import { AppShell } from '@/components/layout/AppShell';
import { LoginPage } from '@/pages/LoginPage';
import { ForbiddenPage } from '@/pages/ForbiddenPage';
import { NotFoundPage } from '@/pages/NotFoundPage';
import { TrackerLandingPage } from '@/pages/tracker/TrackerLandingPage';
import { MeetingsListPage } from '@/pages/tracker/MeetingsListPage';
import { MeetingDetailPage } from '@/pages/tracker/MeetingDetailPage';
import { IssuesListPage } from '@/pages/tracker/IssuesListPage';
import { IssueDetailPage } from '@/pages/tracker/IssueDetailPage';
import { IssueCreatePage } from '@/pages/tracker/IssueCreatePage';
import { IssueEditPage } from '@/pages/tracker/IssueEditPage';
import { MonitoringPage } from '@/pages/tracker/MonitoringPage';
import { OccurrenceFormPage } from '@/pages/tracker/OccurrenceFormPage';
import { ReportsPage } from '@/pages/tracker/ReportsPage';
import { MasterDataPage } from '@/pages/tracker/MasterDataPage';
import { UsersPage } from '@/pages/tracker/UsersPage';
import { SettingsPage } from '@/pages/tracker/SettingsPage';
import { AuditPlaceholderPage } from '@/pages/AuditPlaceholderPage';

export const router = createBrowserRouter([
  { path: '/', element: <Navigate to="/app/dashboard" replace /> },
  { path: '/login', element: <LoginPage /> },
  { path: '/forbidden', element: <ForbiddenPage /> },
  {
    element: <ProtectedRoute />,
    children: [
      {
        path: '/app',
        element: <AppShell />,
        children: [
          { index: true, element: <Navigate to="/app/dashboard" replace /> },
          { path: 'dashboard', element: <TrackerLandingPage /> },
          { path: 'meetings', element: <MeetingsListPage /> },
          // Occurrence authoring stays in the Meetings area, gated Editor/Admin
          // (NOT under the Admin-only navigation section).
          {
            element: <RoleRoute allowedRoles={['EDITOR', 'ADMIN']} />,
            children: [
              { path: 'meetings/new', element: <OccurrenceFormPage /> },
              { path: 'meetings/:meetingId/edit', element: <OccurrenceFormPage /> },
            ],
          },
          { path: 'meetings/:meetingId', element: <MeetingDetailPage /> },
          { path: 'issues', element: <IssuesListPage /> },
          { path: 'issues/new', element: <IssueCreatePage /> },
          { path: 'issues/:issueId', element: <IssueDetailPage /> },
          { path: 'issues/:issueId/edit', element: <IssueEditPage /> },
          { path: 'monitoring/:view', element: <MonitoringPage /> },
          { path: 'reports', element: <ReportsPage /> },
          {
            element: <RoleRoute allowedRoles={['ADMIN']} />,
            children: [
              { path: 'master-data', element: <MasterDataPage /> },
              { path: 'users', element: <UsersPage /> },
              { path: 'audit', element: <AuditPlaceholderPage /> },
              { path: 'settings', element: <SettingsPage /> },
            ],
          },
          { path: '*', element: <NotFoundPage /> },
        ],
      },
    ],
  },
  { path: '*', element: <NotFoundPage /> },
]);
