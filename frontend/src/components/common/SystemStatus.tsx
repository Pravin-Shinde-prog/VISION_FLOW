import React from 'react';
import {
  Server,
  RefreshCw,
  AlertTriangle,
  Clock,
  Globe,
  Tag,
  Layers,
  Terminal,
} from 'lucide-react';
import { SystemStatusState } from '../../types/health';

interface SystemStatusProps {
  statusState: SystemStatusState;
  onRefresh: () => void;
}

export const SystemStatus: React.FC<SystemStatusProps> = ({ statusState, onRefresh }) => {
  const isOnline = statusState.status === 'online';
  const isLoading = statusState.status === 'loading';
  const isOffline = statusState.status === 'offline';

  return (
    <div className="rounded-xl border border-slate-800 bg-[#111827] shadow-lg overflow-hidden">
      {/* Card Header */}
      <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/50">
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
              <span>Backend Core Service Status</span>
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
              Live FastAPI operational status via <code className="text-slate-300 font-mono text-[11px]">GET /api/health</code>
            </p>
          </div>
        </div>

        <button
          onClick={onRefresh}
          disabled={isLoading}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800/80 hover:bg-slate-700 text-xs font-medium text-slate-200 transition-all disabled:opacity-50"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin text-blue-400' : 'text-slate-400'}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Card Content Details */}
      <div className="p-6 space-y-5">
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

        {/* Footer timestamp */}
        <div className="flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-800/80">
          <div className="flex items-center space-x-2">
            <span className="h-1.5 w-1.5 rounded-full bg-slate-600"></span>
            <span>Endpoint: <code className="font-mono text-slate-300">GET /api/health</code></span>
          </div>
          <span>
            Last checked: {statusState.lastChecked ? statusState.lastChecked.toLocaleTimeString() : 'Never'}
          </span>
        </div>
      </div>
    </div>
  );
};
