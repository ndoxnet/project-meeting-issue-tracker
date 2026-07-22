// Concept by MrHan (08974747477)
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { ProtectedRoute } from '@/auth/ProtectedRoute';
import { RoleRoute } from '@/auth/RoleRoute';
import { AppShell } from '@/components/layout/AppShell';
import { LoginPage } from '@/pages/LoginPage';
import { ForbiddenPage } from '@/pages/ForbiddenPage';
import { NotFoundPage } from '@/pages/NotFoundPage';
import { DashboardPlaceholderPage } from '@/pages/DashboardPlaceholderPage';
import { IssuesPlaceholderPage } from '@/pages/IssuesPlaceholderPage';
import { MeetingsPlaceholderPage } from '@/pages/MeetingsPlaceholderPage';
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
          { path: 'dashboard', element: <DashboardPlaceholderPage /> },
          { path: 'issues', element: <IssuesPlaceholderPage /> },
          { path: 'meetings', element: <MeetingsPlaceholderPage /> },
          { path: 'reports', element: <ReportsPlaceholderPage /> },
          {
            element: <RoleRoute allowedRoles={['ADMIN']} />,
            children: [
              { path: 'users', element: <UsersPlaceholderPage /> },
              { path: 'audit', element: <AuditPlaceholderPage /> },
              { path: 'settings', element: <SettingsPlaceholderPage /> },
            ],
          },
          // Unknown path inside the shell.
          { path: '*', element: <NotFoundPage /> },
        ],
      },
    ],
  },
  // Global not-found.
  { path: '*', element: <NotFoundPage /> },
]);
