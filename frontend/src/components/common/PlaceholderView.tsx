import React from 'react';
import { Construction, BookOpen, Layers, CheckCircle2 } from 'lucide-react';

interface PlannedFeature {
  title: string;
  desc: string;
}

interface PlaceholderViewProps {
  title: string;
  stageName: string;
  stageNumber: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
  plannedFeatures: PlannedFeature[];
}

export const PlaceholderView: React.FC<PlaceholderViewProps> = ({
  title,
  stageName,
  stageNumber,
  icon: Icon,
  description,
  plannedFeatures,
}) => {
  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="rounded-xl border border-slate-800 bg-[#111827] p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-4">
            <div className="p-3 rounded-xl bg-blue-600/10 border border-blue-500/20 text-blue-400">
              <Icon className="h-7 w-7" />
            </div>
            <div className="space-y-1">
              <div className="flex items-center space-x-2.5">
                <h1 className="text-xl font-bold text-slate-100 font-mono">{title}</h1>
                <span className="px-2.5 py-0.5 rounded-md text-[11px] font-mono font-semibold bg-blue-950/80 border border-blue-800 text-blue-400">
                  {stageNumber}
                </span>
              </div>
              <p className="text-xs text-slate-400 max-w-3xl leading-relaxed">
                {description}
              </p>
            </div>
          </div>

          <div className="hidden lg:flex items-center space-x-2 px-3 py-1.5 rounded-lg border border-amber-800/60 bg-amber-950/30 text-amber-300 text-xs">
            <Construction className="h-4 w-4 text-amber-400" />
            <span>Scheduled for {stageName}</span>
          </div>
        </div>
      </div>

      {/* Planned Feature Specification Details */}
      <div className="rounded-xl border border-slate-800 bg-[#111827] p-6 space-y-4">
        <div className="flex items-center space-x-2 text-slate-300 font-semibold text-sm">
          <Layers className="h-4 w-4 text-blue-400" />
          <span>Planned Specifications &amp; Architectural Deliverables</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {plannedFeatures.map((feat, idx) => (
            <div
              key={idx}
              className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 space-y-1.5"
            >
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="h-4 w-4 text-slate-500 shrink-0" />
                <h3 className="text-xs font-semibold text-slate-200">{feat.title}</h3>
              </div>
              <p className="text-[11px] text-slate-400 leading-relaxed pl-6">
                {feat.desc}
              </p>
            </div>
          ))}
        </div>

        <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center space-x-2">
            <BookOpen className="h-4 w-4 text-slate-500" />
            <span>Implementation follows the 18-Stage Roadmap in <code className="font-mono text-slate-300">docs/roadmap.md</code></span>
          </div>
          <span className="font-mono text-[11px] text-blue-400 font-medium">Genuine Prototype Logic Only (No Mock UI)</span>
        </div>
      </div>
    </div>
  );
};
