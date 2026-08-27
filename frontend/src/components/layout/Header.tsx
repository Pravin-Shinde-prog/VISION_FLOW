import React, { useState, useEffect } from 'react';
import { Activity, Radio, Clock } from 'lucide-react';
import { HealthStatus } from '../../types/health';

interface HeaderProps {
  backendStatus: HealthStatus;
  latencyMs: number | null;
}

export const Header: React.FC<HeaderProps> = ({ backendStatus, latencyMs }) => {
  const [timeStr, setTimeStr] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toUTCString().replace('GMT', 'UTC'));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-16 border-b border-slate-800 bg-[#0B0F17]/95 backdrop-blur-sm px-6 flex items-center justify-between sticky top-0 z-50">
      {/* Brand & Project Identity */}
      <div className="flex items-center space-x-4">
        <div className="h-9 w-9 rounded-lg bg-blue-600/10 border border-blue-500/30 flex items-center justify-center text-blue-400">
          <Activity className="h-5 w-5" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <span className="font-bold text-lg tracking-wider text-slate-100 font-mono">VISION_FLOW</span>
            <span className="text-[10px] uppercase tracking-widest font-semibold px-2 py-0.5 rounded bg-blue-950/80 border border-blue-800 text-blue-400">
              SIH Prototype
            </span>
          </div>
          <p className="text-xs text-slate-400 font-medium tracking-tight">
            City-Wide AI Traffic Intelligence & ANPR Engine
          </p>
        </div>
      </div>

      {/* Center/Right Status Telemetry */}
      <div className="flex items-center space-x-6 text-xs">
        {/* Real-time Clock */}
        <div className="hidden md:flex items-center space-x-2 text-slate-400 font-mono">
          <Clock className="h-3.5 w-3.5 text-slate-500" />
          <span>{timeStr || 'Synchronizing UTC...'}</span>
        </div>

        {/* Prototype Feed Mode */}
        <div className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 text-slate-300">
          <Radio className="h-3.5 w-3.5 text-amber-400 animate-pulse" />
          <span className="text-[11px] font-medium">Feed Mode: Simulated / Edge Ready</span>
        </div>

        {/* Backend Connectivity Badge */}
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-md bg-slate-900 border border-slate-800">
          <span
            className={`h-2 w-2 rounded-full ${
              backendStatus === 'online'
                ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.6)]'
                : backendStatus === 'loading'
                ? 'bg-amber-400 animate-pulse'
                : 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.6)]'
            }`}
          />
          <div className="flex flex-col">
            <span className="text-[10px] text-slate-400 uppercase font-semibold leading-none">FastAPI Core</span>
            <span
              className={`text-xs font-mono font-medium leading-tight ${
                backendStatus === 'online'
                  ? 'text-emerald-400'
                  : backendStatus === 'loading'
                  ? 'text-amber-400'
                  : 'text-rose-400'
              }`}
            >
              {backendStatus === 'online'
                ? `Online ${latencyMs !== null ? `(${latencyMs}ms)` : ''}`
                : backendStatus === 'loading'
                ? 'Connecting...'
                : 'Offline'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
