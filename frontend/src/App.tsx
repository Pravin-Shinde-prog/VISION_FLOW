import React, { useState, useEffect, useCallback } from 'react';
import { AppLayout } from './components/layout/AppLayout';
import { ViewKey } from './components/layout/Sidebar';
import { DashboardPage } from './pages/DashboardPage';
import { EdgeVisionPage } from './pages/EdgeVisionPage';
import { VehicleTrackingPage } from './pages/VehicleTrackingPage';
import { TrajectoryEnginePage } from './pages/TrajectoryEnginePage';
import { LawEnforcementPage } from './pages/LawEnforcementPage';
import { UrbanAnalyticsPage } from './pages/UrbanAnalyticsPage';
import { CameraNetworkPage } from './pages/CameraNetworkPage';
import { checkBackendHealth, checkDatabaseHealth } from './services/api';
import { SystemStatusState, DatabaseStatusState } from './types/health';

export const App: React.FC = () => {
  const [activeView, setActiveView] = useState<ViewKey>('dashboard');
  const [statusState, setStatusState] = useState<SystemStatusState>({
    status: 'loading',
    data: null,
    error: null,
    lastChecked: null,
    latencyMs: null,
  });
  const [dbStatusState, setDbStatusState] = useState<DatabaseStatusState>({
    status: 'loading',
    data: null,
    error: null,
    latencyMs: null,
  });

  const performHealthCheck = useCallback(async () => {
    setStatusState((prev) => ({ ...prev, status: 'loading' }));
    setDbStatusState((prev) => ({ ...prev, status: 'loading' }));

    // 1. Check FastAPI Backend Health
    try {
      const { data, latencyMs } = await checkBackendHealth();
      setStatusState({
        status: 'online',
        data,
        error: null,
        lastChecked: new Date(),
        latencyMs,
      });
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Backend connection failed';
      setStatusState({
        status: 'offline',
        data: null,
        error: errorMessage,
        lastChecked: new Date(),
        latencyMs: null,
      });
    }

    // 2. Check Database & PostGIS Health
    try {
      const dbData = await checkDatabaseHealth();
      setDbStatusState({
        status: 'online',
        data: dbData,
        error: null,
        latencyMs: dbData.latency_ms,
      });
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Database check failed';
      setDbStatusState({
        status: 'offline',
        data: null,
        error: errorMessage,
        latencyMs: null,
      });
    }
  }, []);

  // Initial check and periodic polling every 10s
  useEffect(() => {
    performHealthCheck();
    const interval = setInterval(performHealthCheck, 10000);
    return () => clearInterval(interval);
  }, [performHealthCheck]);

  const renderActiveView = () => {
    switch (activeView) {
      case 'dashboard':
        return (
          <DashboardPage
            statusState={statusState}
            dbStatusState={dbStatusState}
            onRefreshHealth={performHealthCheck}
            onNavigate={(view) => setActiveView(view)}
          />
        );
      case 'edge-vision':
        return <EdgeVisionPage />;
      case 'vehicle-tracking':
        return <VehicleTrackingPage />;
      case 'trajectory-engine':
        return <TrajectoryEnginePage />;
      case 'law-enforcement':
        return <LawEnforcementPage />;
      case 'urban-analytics':
        return <UrbanAnalyticsPage />;
      case 'camera-network':
        return <CameraNetworkPage />;
      default:
        return (
          <DashboardPage
            statusState={statusState}
            dbStatusState={dbStatusState}
            onRefreshHealth={performHealthCheck}
            onNavigate={(view) => setActiveView(view)}
          />
        );
    }
  };

  return (
    <AppLayout
      activeView={activeView}
      onSelectView={setActiveView}
      backendStatus={statusState.status}
      latencyMs={statusState.latencyMs}
    >
      {renderActiveView()}
    </AppLayout>
  );
};

export default App;
