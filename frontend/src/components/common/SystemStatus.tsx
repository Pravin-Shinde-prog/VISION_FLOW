import React from 'react';
import {
  Server,
  Database,
  RefreshCw,
  Clock,
  Globe,
  Tag,
  Layers,
  Terminal,
  MapPin,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';
import { SystemStatusState, DatabaseStatusState } from '../../types/health';

interface SystemStatusProps {
  statusState: SystemStatusState;
  dbStatusState?: DatabaseStatusState;
  onRefresh: () => void;
}

export const SystemStatus: React.FC<SystemStatusProps> = ({
  statusState,
  dbStatusState,
  onRefresh,
}) => {
  const isOnline = statusState.status === 'online';
  const isLoading = statusState.status === 'loading';
  const isOffline = statusState.status === 'offline';

  const isDbOnline = dbStatusState?.status === 'online';
  const isDbLoading = dbStatusState?.status === 'loading';

  return (
    <div className="rounded-xl border border-slate-800 bg-[#111827] shadow-lg overflow-hidden space-y-px bg-slate-800">
      {/* 1. FastAPI Core Service Health */}
      <div className="bg-[#111827]">
        <div className="px-6 py-4 border-b border-slate-800/80 flex items-center justify-between bg-slate-900/50">
          <div className="flex items-center space-x-3">
            <div
              className={`p-2 rounded-lg border ${
                isOnline
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                  : isLoading
                  ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
                  : 'bg-rose-500/10 border-rose-500/30 text-rose-400'
              }`}
            >
              <Server className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-100 flex items-center space-x-2">
                <span>FastAPI Backend Core</span>
                <span
                  className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full uppercase border ${
                    isOnline
                      ? 'bg-emerald-950/70 border-emerald-700 text-emerald-300'
                      : isLoading
                      ? 'bg-amber-950/70 border-amber-700 text-amber-300'
                      : 'bg-rose-950/70 border-rose-700 text-rose-300'
                  }`}
                >
                  {isLoading ? 'Checking' : isOnline ? 'Online' : 'Offline'}
                </span>
              </h3>
              <p className="text-xs text-slate-400">
                Operational status via <code className="text-slate-300 font-mono text-[11px]">GET /api/health</code>
              </p>
            </div>
          </div>

          <button
            onClick={onRefresh}
            disabled={isLoading || isDbLoading}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800/80 hover:bg-slate-700 text-xs font-medium text-slate-200 transition-all disabled:opacity-50"
          >
            <RefreshCw
              className={`h-3.5 w-3.5 ${
                isLoading || isDbLoading ? 'animate-spin text-blue-400' : 'text-slate-400'
              }`}
            />
            <span>Refresh All</span>
          </button>
        </div>

        <div className="p-6 space-y-4">
          {isOnline && statusState.data && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-3.5 rounded-lg bg-slate-900/70 border border-slate-800 space-y-1">
                <div className="flex items-center space-x-2 text-slate-400 text-xs">
                  <Tag className="h-3.5 w-3.5 text-blue-400" />
                  <span>Service Identifier</span>
                </div>
                <p className="text-sm font-semibold text-slate-200 font-mono truncate">
                  {statusState.data.service}
                </p>
              </div>

              <div className="p-3.5 rounded-lg bg-slate-900/70 border border-slate-800 space-y-1">
                <div className="flex items-center space-x-2 text-slate-400 text-xs">
                  <Layers className="h-3.5 w-3.5 text-emerald-400" />
                  <span>API Version</span>
                </div>
                <p className="text-sm font-semibold text-slate-200 font-mono">
                  v{statusState.data.version}
                </p>
              </div>

              <div className="p-3.5 rounded-lg bg-slate-900/70 border border-slate-800 space-y-1">
                <div className="flex items-center space-x-2 text-slate-400 text-xs">
                  <Clock className="h-3.5 w-3.5 text-purple-400" />
                  <span>Roundtrip Latency</span>
                </div>
                <p className="text-sm font-semibold text-emerald-400 font-mono">
                  {statusState.latencyMs !== null ? `${statusState.latencyMs} ms` : '—'}
                </p>
              </div>

              <div className="p-3.5 rounded-lg bg-slate-900/70 border border-slate-800 space-y-1">
                <div className="flex items-center space-x-2 text-slate-400 text-xs">
                  <Globe className="h-3.5 w-3.5 text-amber-400" />
                  <span>Environment</span>
                </div>
                <p className="text-sm font-semibold text-slate-200 font-mono capitalize">
                  {statusState.data.environment}
                </p>
              </div>
            </div>
          )}

          {isOffline && (
            <div className="rounded-lg border border-rose-900/60 bg-rose-950/20 p-4 space-y-3">
              <div className="flex items-start space-x-3">
                <AlertTriangle className="h-5 w-5 text-rose-400 shrink-0 mt-0.5" />
                <div>
                  <h4 className="text-sm font-semibold text-rose-300">Backend Unreachable</h4>
                  <p className="text-xs text-rose-400/90 mt-0.5">
                    The frontend was unable to connect to the FastAPI backend service at <code className="font-mono bg-rose-950 px-1 py-0.5 rounded">/api/health</code>.
                  </p>
                  {statusState.error && (
                    <p className="text-[11px] text-slate-400 font-mono mt-1">
                      Error details: {statusState.error}
                    </p>
                  )}
                </div>
              </div>

              <div className="p-3 rounded bg-slate-950/80 border border-slate-800 text-xs text-slate-300 space-y-2">
                <div className="flex items-center space-x-2 text-slate-400 font-mono text-[11px]">
                  <Terminal className="h-3.5 w-3.5 text-blue-400" />
                  <span>To launch the backend server in WSL:</span>
                </div>
                <code className="block font-mono text-emerald-400 text-xs bg-slate-900 px-2.5 py-1.5 rounded border border-slate-800">
                  cd backend &amp;&amp; source .venv/bin/activate &amp;&amp; uvicorn app.main:app --reload --port 8000
                </code>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 2. PostgreSQL + PostGIS Spatial Database Health */}
      <div className="bg-[#111827]">
        <div className="px-6 py-4 border-b border-slate-800/80 flex items-center justify-between bg-slate-900/40">
          <div className="flex items-center space-x-3">
            <div
              className={`p-2 rounded-lg border ${
                isDbOnline
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                  : isDbLoading
                  ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
                  : 'bg-rose-500/10 border-rose-500/30 text-rose-400'
              }`}
            >
              <Database className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-100 flex items-center space-x-2">
                <span>PostgreSQL &amp; PostGIS Spatial Layer</span>
                <span
                  className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full uppercase border ${
                    isDbOnline
                      ? 'bg-emerald-950/70 border-emerald-700 text-emerald-300'
                      : isDbLoading
                      ? 'bg-amber-950/70 border-amber-700 text-amber-300'
                      : 'bg-rose-950/70 border-rose-700 text-rose-300'
                  }`}
                >
                  {isDbLoading ? 'Checking' : isDbOnline ? 'Connected' : 'Unavailable'}
                </span>
              </h3>
              <p className="text-xs text-slate-400">
                Spatial queries via <code className="text-slate-300 font-mono text-[11px]">GET /api/v1/health/database</code>
              </p>
            </div>
          </div>
        </div>

        <div className="p-6">
          {isDbOnline && dbStatusState?.data && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="p-3.5 rounded-lg bg-slate-900/70 border border-slate-800 space-y-1">
                <div className="flex items-center space-x-2 text-slate-400 text-xs">
                  <Database className="h-3.5 w-3.5 text-blue-400" />
                  <span>Database Name</span>
                </div>
                <p className="text-sm font-semibold text-slate-200 font-mono">
                  {dbStatusState.data.database}
                </p>
              </div>

              <div className="p-3.5 rounded-lg bg-slate-900/70 border border-slate-800 space-y-1">
                <div className="flex items-center space-x-2 text-slate-400 text-xs">
                  <MapPin className="h-3.5 w-3.5 text-emerald-400" />
                  <span>PostGIS Extension</span>
                </div>
                <p className="text-xs font-semibold text-emerald-400 font-mono truncate" title={dbStatusState.data.postgis_version || ''}>
                  {dbStatusState.data.postgis_version || 'Enabled'}
                </p>
              </div>

              <div className="p-3.5 rounded-lg bg-slate-900/70 border border-slate-800 space-y-1">
                <div className="flex items-center space-x-2 text-slate-400 text-xs">
                  <Clock className="h-3.5 w-3.5 text-purple-400" />
                  <span>DB Query Latency</span>
                </div>
                <p className="text-sm font-semibold text-emerald-400 font-mono">
                  {dbStatusState.data.latency_ms !== null ? `${dbStatusState.data.latency_ms} ms` : '—'}
                </p>
              </div>
            </div>
          )}

          {!isDbOnline && !isDbLoading && (
            <div className="rounded-lg border border-rose-900/60 bg-rose-950/20 p-4 space-y-2">
              <div className="flex items-start space-x-3">
                <AlertTriangle className="h-5 w-5 text-rose-400 shrink-0 mt-0.5" />
                <div>
                  <h4 className="text-sm font-semibold text-rose-300">Database Connection Failed</h4>
                  <p className="text-xs text-rose-400/90 mt-0.5">
                    FastAPI could not complete query <code className="font-mono bg-rose-950 px-1 py-0.5 rounded">SELECT current_database(), PostGIS_Version();</code>.
                  </p>
                  {dbStatusState?.error && (
                    <p className="text-[11px] text-slate-400 font-mono mt-1">
                      Details: {dbStatusState.error}
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Footer timestamp */}
          <div className="flex items-center justify-between text-[11px] text-slate-400 pt-3 mt-4 border-t border-slate-800/80">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="h-3.5 w-3.5 text-slate-500" />
              <span>Driver: <code className="font-mono text-slate-300">SQLAlchemy 2.0 (asyncpg)</code></span>
            </div>
            <span>
              Last checked: {statusState.lastChecked ? statusState.lastChecked.toLocaleTimeString() : 'Never'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
