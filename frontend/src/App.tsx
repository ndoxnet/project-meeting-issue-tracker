// Concept by MrHan (08974747477)
import { Routes, Route } from 'react-router-dom';
import AppShell from '@/layouts/AppShell';
import Login from '@/pages/Login';
import Dashboard from '@/pages/Dashboard';
import Issues from '@/pages/Issues';
import IssueDetail from '@/pages/IssueDetail';
import Meetings from '@/pages/Meetings';
import Overdue from '@/pages/Overdue';
import Reports from '@/pages/Reports';
import MasterData from '@/pages/MasterData';
import Users from '@/pages/Users';
import AuditLog from '@/pages/AuditLog';
import Settings from '@/pages/Settings';
import NotFound from '@/pages/NotFound';

// Phase 3 adds an auth guard around the AppShell routes.
export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<AppShell />}>
        <Route index element={<Dashboard />} />
        <Route path="issues" element={<Issues />} />
        <Route path="issues/:id" element={<IssueDetail />} />
        <Route path="meetings" element={<Meetings />} />
        <Route path="overdue" element={<Overdue />} />
        <Route path="reports" element={<Reports />} />
        <Route path="master-data" element={<MasterData />} />
        <Route path="users" element={<Users />} />
        <Route path="audit-log" element={<AuditLog />} />
        <Route path="settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
