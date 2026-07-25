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
import { ReportsPlaceholderPage } from '@/pages/ReportsPlaceholderPage';
import { UsersPlaceholderPage } from '@/pages/UsersPlaceholderPage';
import { AuditPlaceholderPage } from '@/pages/AuditPlaceholderPage';
import { SettingsPlaceholderPage } from '@/pages/SettingsPlaceholderPage';

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
          { path: 'meetings/:meetingId', element: <MeetingDetailPage /> },
          { path: 'issues', element: <IssuesListPage /> },
          { path: 'issues/new', element: <IssueCreatePage /> },
          { path: 'issues/:issueId', element: <IssueDetailPage /> },
          { path: 'issues/:issueId/edit', element: <IssueEditPage /> },
          { path: 'reports', element: <ReportsPlaceholderPage /> },
          {
            element: <RoleRoute allowedRoles={['ADMIN']} />,
            children: [
              { path: 'users', element: <UsersPlaceholderPage /> },
              { path: 'audit', element: <AuditPlaceholderPage /> },
              { path: 'settings', element: <SettingsPlaceholderPage /> },
            ],
          },
          { path: '*', element: <NotFoundPage /> },
        ],
      },
    ],
  },
  { path: '*', element: <NotFoundPage /> },
]);
