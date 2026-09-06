import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

import { useAuth } from '../context/AuthContext';
import { OwnerLayout } from '../layouts/OwnerLayout';
import { SalesLayout } from '../layouts/SalesLayout';

import { LoginPage } from '../pages/auth/LoginPage';
import { OwnerDashboard } from '../pages/owner/OwnerDashboard';
import { OwnerLeads } from '../pages/owner/OwnerLeads';
import { OwnerLeadDetail } from '../pages/owner/OwnerLeadDetail';
import { QualificationRulesPage } from '../pages/owner/QualificationRulesPage';
import { TeamPage } from '../pages/owner/TeamPage';
import { AnalyticsPage } from '../pages/owner/AnalyticsPage';
import { AutomationsPage } from '../pages/owner/AutomationsPage';
import { SettingsPage } from '../pages/owner/SettingsPage';

import { SalesDashboard } from '../pages/sales/SalesDashboard';
import { SalesLeads } from '../pages/sales/SalesLeads';
import { SalesLeadDetail } from '../pages/sales/SalesLeadDetail';
import { FollowUpsPage } from '../pages/sales/FollowUpsPage';
import { ProfilePage } from '../pages/sales/ProfilePage';
import { LoadingSpinner } from '../components/ui/LoadingState';

const ProtectedRoute: React.FC<{
  children: React.ReactNode;
  allowedRoles?: string[];
}> = ({ children, allowedRoles }) => {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div className="min-h-screen bg-slate-900 flex items-center justify-center"><LoadingSpinner text="Authenticating..." /></div>;
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to={user.role === 'BRAND_OWNER' ? '/owner/dashboard' : '/sales/dashboard'} replace />;
  }

  return <>{children}</>;
};

export const AppRoutes: React.FC = () => {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div className="min-h-screen bg-slate-900 flex items-center justify-center"><LoadingSpinner text="Initializing Platform..." /></div>;
  }

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      {/* Owner Portal Routes */}
      <Route
        path="/owner"
        element={
          <ProtectedRoute allowedRoles={['BRAND_OWNER']}>
            <OwnerLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/owner/dashboard" replace />} />
        <Route path="dashboard" element={<OwnerDashboard />} />
        <Route path="leads" element={<OwnerLeads />} />
        <Route path="leads/:id" element={<OwnerLeadDetail />} />
        <Route path="analytics" element={<AnalyticsPage />} />
        <Route path="team" element={<TeamPage />} />
        <Route path="rules" element={<QualificationRulesPage />} />
        <Route path="automations" element={<AutomationsPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>

      {/* Sales Portal Routes */}
      <Route
        path="/sales"
        element={
          <ProtectedRoute allowedRoles={['SALES_AGENT', 'SALES_MANAGER', 'BRAND_OWNER']}>
            <SalesLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/sales/dashboard" replace />} />
        <Route path="dashboard" element={<SalesDashboard />} />
        <Route path="leads" element={<SalesLeads />} />
        <Route path="leads/:id" element={<SalesLeadDetail />} />
        <Route path="followups" element={<FollowUpsPage />} />
        <Route path="profile" element={<ProfilePage />} />
      </Route>

      {/* Default Root Redirect */}
      <Route
        path="*"
        element={
          isAuthenticated ? (
            user?.role === 'BRAND_OWNER' ? (
              <Navigate to="/owner/dashboard" replace />
            ) : (
              <Navigate to="/sales/dashboard" replace />
            )
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
    </Routes>
  );
};
