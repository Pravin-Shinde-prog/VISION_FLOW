import React from 'react';
import { Header } from './Header';
import { Sidebar, ViewKey } from './Sidebar';
import { HealthStatus } from '../../types/health';

interface AppLayoutProps {
  activeView: ViewKey;
  onSelectView: (key: ViewKey) => void;
  backendStatus: HealthStatus;
  latencyMs: number | null;
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({
  activeView,
  onSelectView,
  backendStatus,
  latencyMs,
  children,
}) => {
  return (
    <div className="min-h-screen flex flex-col bg-[#0B0F17] text-slate-100">
      <Header backendStatus={backendStatus} latencyMs={latencyMs} />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar activeView={activeView} onSelectView={onSelectView} />
        <main className="flex-1 overflow-y-auto bg-[#0B0F17] p-6 lg:p-8">
          <div className="max-w-7xl mx-auto space-y-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};
