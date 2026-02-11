import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { RequirePerm } from './auth/RequirePerm';
import { useAuthStore } from './auth/store';
import { NavLayout } from './components/NavLayout';
import { AdminPage } from './pages/AdminPage';
import { AIInsightsPage } from './pages/AIInsightsPage';
import { AlertsPage } from './pages/AlertsPage';
import { ClusterOverviewPage } from './pages/ClusterOverviewPage';
import { KafkaPage } from './pages/KafkaPage';
import { LoginPage } from './pages/LoginPage';
import { NamespacesPage } from './pages/NamespacesPage';
import { SparkPage } from './pages/SparkPage';
import { WorkloadsPage } from './pages/WorkloadsPage';
import './styles.css';

const queryClient = new QueryClient();

function Protected({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.accessToken);
  if (!token) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <Protected>
                <NavLayout />
              </Protected>
            }
          >
            <Route index element={<ClusterOverviewPage />} />
            <Route path="namespaces" element={<NamespacesPage />} />
            <Route path="workloads" element={<WorkloadsPage />} />
            <Route path="spark" element={<RequirePerm perm="spark.deploy"><SparkPage /></RequirePerm>} />
            <Route path="kafka" element={<RequirePerm perm="kafka.deploy"><KafkaPage /></RequirePerm>} />
            <Route path="alerts" element={<RequirePerm perm="alerts.manage"><AlertsPage /></RequirePerm>} />
            <Route path="ai" element={<RequirePerm perm="ai.use"><AIInsightsPage /></RequirePerm>} />
            <Route path="admin" element={<RequirePerm perm="admin.rbac.read"><AdminPage /></RequirePerm>} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>,
);
