import React from 'react';
import {
  LayoutDashboard,
  Cpu,
  Car,
  GitFork,
  ShieldAlert,
  BarChart3,
  Video,
} from 'lucide-react';

export type ViewKey =
  | 'dashboard'
  | 'edge-vision'
  | 'vehicle-tracking'
  | 'trajectory-engine'
  | 'law-enforcement'
  | 'urban-analytics'
  | 'camera-network';

interface NavItem {
  key: ViewKey;
  label: string;
  stageBadge?: string;
  icon: React.ComponentType<{ className?: string }>;
}

interface SidebarProps {
  activeView: ViewKey;
  onSelectView: (key: ViewKey) => void;
}

const navItems: NavItem[] = [
  { key: 'dashboard', label: 'Command Center', icon: LayoutDashboard },
  { key: 'edge-vision', label: 'Edge Vision & ANPR', stageBadge: 'Stage 7-8', icon: Cpu },
  { key: 'vehicle-tracking', label: 'Vehicle Re-ID', stageBadge: 'Stage 9-10', icon: Car },
  { key: 'trajectory-engine', label: 'Spatio-Temporal Graph', stageBadge: 'Stage 11-12', icon: GitFork },
  { key: 'law-enforcement', label: 'Law Enforcement & Alerts', stageBadge: 'Stage 13', icon: ShieldAlert },
  { key: 'urban-analytics', label: 'Urban Traffic Analytics', stageBadge: 'Stage 14', icon: BarChart3 },
  { key: 'camera-network', label: 'Camera GIS Network', stageBadge: 'Stage 6', icon: Video },
];

export const Sidebar: React.FC<SidebarProps> = ({ activeView, onSelectView }) => {
  return (
    <aside className="w-64 border-r border-slate-800 bg-[#0E131F] flex flex-col justify-between shrink-0 select-none">
      {/* Navigation Links */}
      <div className="p-4 space-y-6">
        <div>
          <p className="px-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-2">
            Operations Console
          </p>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeView === item.key;

              return (
                <button
                  key={item.key}
                  onClick={() => onSelectView(item.key)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 shadow-[0_0_12px_rgba(59,130,246,0.15)]'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-transparent'
                  }`}
                >
                  <div className="flex items-center space-x-3 truncate">
                    <Icon className={`h-4 w-4 shrink-0 ${isActive ? 'text-blue-400' : 'text-slate-400'}`} />
                    <span className="truncate">{item.label}</span>
                  </div>
                  {item.stageBadge && (
                    <span
                      className={`text-[9px] font-mono px-1.5 py-0.5 rounded border ${
                        isActive
                          ? 'bg-blue-900/50 border-blue-700 text-blue-300'
                          : 'bg-slate-900 border-slate-800 text-slate-400'
                      }`}
                    >
                      {item.stageBadge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* System Stage Metadata Footer */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/40">
        <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[10px] uppercase font-bold text-slate-400">Current Phase</span>
            <span className="text-[10px] font-mono text-emerald-400 font-semibold bg-emerald-950/60 border border-emerald-800/80 px-1.5 py-0.5 rounded">
              Active
            </span>
          </div>
          <p className="text-xs font-semibold text-slate-200">Stage 3-4 Foundation</p>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            Frontend UI Shell + FastAPI backend communication pipeline established.
          </p>
        </div>
      </div>
    </aside>
  );
};
