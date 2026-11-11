import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Layout } from './components/Layout';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Workspaces } from './pages/Workspaces';
import { Projects } from './pages/Projects';
import { Tasks } from './pages/Tasks';
import { Risks } from './pages/Risks';
import { UserManagement } from './pages/Users';
import { AuditLogs } from './pages/AuditLogs';
import { HealthView } from './pages/SystemHealth';
import { Settings } from './pages/Settings';
import { Releases } from './pages/Releases';
import { Discussions } from './pages/Discussions';
import { CalendarView } from './pages/CalendarView';
import { Broadcast } from './pages/Broadcast';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <div className="min-h-screen bg-[#F4F2E9] flex items-center justify-center text-xs font-semibold text-[#5A6258]">
        Authenticating session...
      </div>
    );
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="discussions" element={<Navigate to="/users?tab=discussions" replace />} />
            <Route path="workspaces" element={<Workspaces />} />
            <Route path="projects" element={<Projects />} />
            <Route path="tasks" element={<Tasks />} />
            <Route path="calendar" element={<CalendarView />} />
            <Route path="broadcast" element={<Broadcast />} />
            <Route path="risks" element={<Risks />} />
            <Route path="users" element={<UserManagement />} />
            <Route path="releases" element={<Releases />} />
            <Route path="audit-logs" element={<AuditLogs />} />
            <Route path="health" element={<HealthView />} />
            <Route path="settings" element={<Settings />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
