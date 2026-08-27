import React from 'react';
import {
  Cpu,
  Car,
  GitFork,
  ShieldAlert,
  BarChart3,
  Video,
  Activity,
  ArrowRight,
  Radio,
} from 'lucide-react';
import { SystemStatus } from '../components/common/SystemStatus';
import { SystemStatusState } from '../types/health';
import { ViewKey } from '../components/layout/Sidebar';

interface DashboardPageProps {
  statusState: SystemStatusState;
  onRefreshHealth: () => void;
  onNavigate: (view: ViewKey) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  statusState,
  onRefreshHealth,
  onNavigate,
}) => {
  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="rounded-xl border border-slate-800 bg-gradient-to-r from-[#111827] via-[#131C31] to-[#111827] p-6 lg:p-8 shadow-xl">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div className="space-y-2 max-w-3xl">
            <div className="flex items-center space-x-2">
              <span className="h-2 w-2 rounded-full bg-blue-500 animate-ping" />
              <span className="text-xs font-mono font-semibold uppercase tracking-widest text-blue-400">
                Central Operations Console
              </span>
            </div>
            <h1 className="text-2xl lg:text-3xl font-extrabold tracking-tight text-white font-mono">
              VISION_FLOW
            </h1>
            <p className="text-sm text-slate-300 leading-relaxed font-light">
              City-Wide AI Engine for Multi-Camera ANPR Trajectory Tracking and Urban Traffic Analytics.
              Built for high-density metropolitan surveillance with graph-validated spatio-temporal tracking,
              cloned-plate anomaly detection, and real-time corridor intelligence.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row lg:flex-col gap-2.5 shrink-0">
            <div className="px-4 py-2.5 rounded-lg bg-slate-900/90 border border-slate-800 flex items-center space-x-3">
              <Activity className="h-4 w-4 text-emerald-400 shrink-0" />
              <div className="text-xs">
                <p className="text-slate-400 text-[10px] uppercase font-bold">Prototype Target</p>
                <p className="font-semibold text-slate-200">Smart India Hackathon (SIH)</p>
              </div>
            </div>
            <div className="px-4 py-2.5 rounded-lg bg-slate-900/90 border border-slate-800 flex items-center space-x-3">
              <Radio className="h-4 w-4 text-blue-400 shrink-0" />
              <div className="text-xs">
                <p className="text-slate-400 text-[10px] uppercase font-bold">Data Ingestion</p>
                <p className="font-semibold text-slate-200">Simulated / Prerecorded Ready</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Real-time Health Check Section */}
      <SystemStatus statusState={statusState} onRefresh={onRefreshHealth} />

      {/* Feature Groups Status Overview */}
      <div className="rounded-xl border border-slate-800 bg-[#111827] p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-semibold text-slate-100 flex items-center space-x-2">
              <span>Five Core Feature Groups</span>
              <span className="text-[11px] font-mono text-slate-400 font-normal">
                (Architectural Breakdown)
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Interactive operations modules mapped to their implementation roadmap milestones.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Card 1 */}
          <div
            onClick={() => onNavigate('edge-vision')}
            className="group p-4 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-blue-500/50 hover:bg-slate-800/40 transition-all cursor-pointer space-y-3"
          >
            <div className="flex items-center justify-between">
              <div className="p-2 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400">
                <Cpu className="h-5 w-5" />
              </div>
              <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-400">
                Stage 7-8
              </span>
            </div>
            <div>
              <h3 className="text-xs font-bold text-slate-200 group-hover:text-blue-400 transition-colors">
                1. Smart Edge Vision &amp; ANPR
              </h3>
              <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                Adaptive contrast/glare enhancement, license plate localization, PaddleOCR, and RTO plate format compliance.
              </p>
            </div>
            <div className="flex items-center text-[11px] text-blue-400 font-medium pt-1">
              <span>View Specs</span>
              <ArrowRight className="h-3 w-3 ml-1 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>

          {/* Card 2 */}
          <div
            onClick={() => onNavigate('vehicle-tracking')}
            className="group p-4 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-emerald-500/50 hover:bg-slate-800/40 transition-all cursor-pointer space-y-3"
          >
            <div className="flex items-center justify-between">
              <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                <Car className="h-5 w-5" />
              </div>
              <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-400">
                Stage 9-10
              </span>
            </div>
            <div>
              <h3 className="text-xs font-bold text-slate-200 group-hover:text-emerald-400 transition-colors">
                2. Multi-Feature Vehicle Re-ID
              </h3>
              <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                Vehicle color, type, window tint, stickers, and physical damage signatures for continuous tracking under plate occlusion.
              </p>
            </div>
            <div className="flex items-center text-[11px] text-emerald-400 font-medium pt-1">
              <span>View Specs</span>
              <ArrowRight className="h-3 w-3 ml-1 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>

          {/* Card 3 */}
          <div
            onClick={() => onNavigate('trajectory-engine')}
            className="group p-4 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-purple-500/50 hover:bg-slate-800/40 transition-all cursor-pointer space-y-3"
          >
            <div className="flex items-center justify-between">
              <div className="p-2 rounded-lg bg-purple-500/10 border border-purple-500/20 text-purple-400">
                <GitFork className="h-5 w-5" />
              </div>
              <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-400">
                Stage 11-12
              </span>
            </div>
            <div>
              <h3 className="text-xs font-bold text-slate-200 group-hover:text-purple-400 transition-colors">
                3. Spatio-Temporal Graph Engine
              </h3>
              <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                Directed road graph validation, travel time constraints, trajectory reconstruction, and ghost/cloned plate detection.
              </p>
            </div>
            <div className="flex items-center text-[11px] text-purple-400 font-medium pt-1">
              <span>View Specs</span>
              <ArrowRight className="h-3 w-3 ml-1 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>

          {/* Card 4 */}
          <div
            onClick={() => onNavigate('law-enforcement')}
            className="group p-4 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-rose-500/50 hover:bg-slate-800/40 transition-all cursor-pointer space-y-3"
          >
            <div className="flex items-center justify-between">
              <div className="p-2 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400">
                <ShieldAlert className="h-5 w-5" />
              </div>
              <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-400">
                Stage 13
              </span>
            </div>
            <div>
              <h3 className="text-xs font-bold text-slate-200 group-hover:text-rose-400 transition-colors">
                4. Law Enforcement Operations
              </h3>
              <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                Stolen vehicle watchlists, high-priority instant push alerts, chronological GIS route history, and forensic audit snapshots.
              </p>
            </div>
            <div className="flex items-center text-[11px] text-rose-400 font-medium pt-1">
              <span>View Specs</span>
              <ArrowRight className="h-3 w-3 ml-1 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>

          {/* Card 5 */}
          <div
            onClick={() => onNavigate('urban-analytics')}
            className="group p-4 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-amber-500/50 hover:bg-slate-800/40 transition-all cursor-pointer space-y-3"
          >
            <div className="flex items-center justify-between">
              <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400">
                <BarChart3 className="h-5 w-5" />
              </div>
              <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-400">
                Stage 14
              </span>
            </div>
            <div>
              <h3 className="text-xs font-bold text-slate-200 group-hover:text-amber-400 transition-colors">
                5. Urban Traffic &amp; Choke Points
              </h3>
              <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                Road segment density, choke-point index, corridor delay heatmaps, and priority emergency green corridors.
              </p>
            </div>
            <div className="flex items-center text-[11px] text-amber-400 font-medium pt-1">
              <span>View Specs</span>
              <ArrowRight className="h-3 w-3 ml-1 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>

          {/* Card 6 */}
          <div
            onClick={() => onNavigate('camera-network')}
            className="group p-4 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-cyan-500/50 hover:bg-slate-800/40 transition-all cursor-pointer space-y-3"
          >
            <div className="flex items-center justify-between">
              <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
                <Video className="h-5 w-5" />
              </div>
              <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-400">
                Stage 6
              </span>
            </div>
            <div>
              <h3 className="text-xs font-bold text-slate-200 group-hover:text-cyan-400 transition-colors">
                GIS Camera Network &amp; Feeds
              </h3>
              <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                Interactive city map, camera node locations, field of view orientation, and simulated feed channels.
              </p>
            </div>
            <div className="flex items-center text-[11px] text-cyan-400 font-medium pt-1">
              <span>View Specs</span>
              <ArrowRight className="h-3 w-3 ml-1 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
