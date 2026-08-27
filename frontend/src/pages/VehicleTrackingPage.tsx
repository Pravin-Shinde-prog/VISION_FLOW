import React, { useState, useEffect, useCallback } from 'react';
import {
  Car,
  RefreshCw,
  Sparkles,
  ShieldCheck,
  Clock,
  Zap,
  Sliders,
  CheckCircle2,
  Layers,
  MapPin,
  AlertCircle
} from 'lucide-react';
import {
  matchVehicleObservations,
  fetchReIDDemoScenario,
} from '../services/api';
import {
  ReIDMatchRequest,
  ReIDMatchResult,
  ReIDDemoScenarioResponse,
  VehicleVisualSignature,
} from '../types/reid';

export const VehicleTrackingPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'journey' | 'matcher'>('journey');
  const [demoData, setDemoData] = useState<ReIDDemoScenarioResponse | null>(null);
  const [isLoadingDemo, setIsLoadingDemo] = useState<boolean>(false);
  const [demoError, setDemoError] = useState<string | null>(null);

  // Interactive Pairwise Matcher State
  const [sourceColor, setSourceColor] = useState<string>('white');
  const [sourceType, setSourceType] = useState<string>('sedan');
  const [sourcePlate, setSourcePlate] = useState<string>('MH12AB1234');
  const [sourcePlateReadable, setSourcePlateReadable] = useState<boolean>(true);

  const [targetColor, setTargetColor] = useState<string>('white');
  const [targetType, setTargetType] = useState<string>('sedan');
  const [targetPlate, setTargetPlate] = useState<string>('');
  const [targetPlateReadable, setTargetPlateReadable] = useState<boolean>(false);

  const [matchResult, setMatchResult] = useState<ReIDMatchResult | null>(null);
  const [isMatching, setIsMatching] = useState<boolean>(false);

  const loadDemoScenario = useCallback(async () => {
    setIsLoadingDemo(true);
    setDemoError(null);
    try {
      const data = await fetchReIDDemoScenario();
      setDemoData(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load demo scenario';
      setDemoError(msg);
    } finally {
      setIsLoadingDemo(false);
    }
  }, []);

  const executePairwiseMatch = useCallback(async () => {
    setIsMatching(true);
    try {
      const sigSource: VehicleVisualSignature = {
        vehicle_color: sourceColor,
        color_confidence: 0.95,
        vehicle_type: sourceType,
        type_confidence: 0.90,
        make: 'Honda',
        model: 'City',
        aspect_ratio: 1.6,
        distinctive_features: ['roof_rails_none'],
        plate_number: sourcePlateReadable ? sourcePlate : null,
        ocr_confidence: sourcePlateReadable ? 0.95 : 0.0,
      };

      const sigTarget: VehicleVisualSignature = {
        vehicle_color: targetColor,
        color_confidence: 0.92,
        vehicle_type: targetType,
        type_confidence: 0.88,
        make: 'Honda',
        model: 'City',
        aspect_ratio: 1.6,
        distinctive_features: ['roof_rails_none'],
        plate_number: targetPlateReadable ? targetPlate : null,
        ocr_confidence: targetPlateReadable ? 0.90 : 0.0,
      };

      const req: ReIDMatchRequest = {
        source: {
          observation_id: 'OBS_SRC',
          camera_id: 'CAM_PUN_001',
          timestamp: new Date().toISOString(),
          signature: sigSource,
          lat: 18.5167,
          lon: 73.8415,
        },
        target: {
          observation_id: 'OBS_TGT',
          camera_id: 'CAM_PUN_002',
          timestamp: new Date(Date.now() + 74000).toISOString(),
          signature: sigTarget,
          lat: 18.5204,
          lon: 73.8432,
        },
      };

      const res = await matchVehicleObservations(req);
      setMatchResult(res);
    } catch {
      // Fallback
    } finally {
      setIsMatching(false);
    }
  }, [sourceColor, sourceType, sourcePlate, sourcePlateReadable, targetColor, targetType, targetPlate, targetPlateReadable]);

  useEffect(() => {
    loadDemoScenario();
    executePairwiseMatch();
  }, [loadDemoScenario, executePairwiseMatch]);

  const getClassificationBadge = (classification: string) => {
    switch (classification) {
      case 'HIGH_CONFIDENCE_MATCH':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'POSSIBLE_MATCH':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
      case 'LOW_CONFIDENCE':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      default:
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
    }
  };

  return (
    <div className="space-y-6 text-slate-100">
      {/* Top Banner */}
      <div className="rounded-xl border border-slate-800 bg-gradient-to-r from-[#111827] via-[#131C31] to-[#111827] p-6 lg:p-8 shadow-xl">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div className="space-y-2 max-w-3xl">
            <div className="flex items-center space-x-2">
              <span className="h-2 w-2 rounded-full bg-blue-500 animate-ping" />
              <span className="text-xs font-mono font-semibold uppercase tracking-widest text-blue-400">
                Stage 10 • Multi-Feature Vehicle Tracking &amp; Re-ID
              </span>
            </div>
            <h1 className="text-2xl lg:text-3xl font-extrabold tracking-tight text-white font-mono flex items-center gap-3">
              <Car className="w-8 h-8 text-blue-400" />
              <span>Multi-Feature Vehicle Re-Identification</span>
            </h1>
            <p className="text-sm text-slate-300 leading-relaxed font-light">
              Maintains unbroken vehicle identity across city camera corridors when license plates are occluded by road mud,
              extreme headlight glare, or physical damage using multi-feature visual similarity.
            </p>
          </div>

          <div className="flex flex-wrap lg:flex-col gap-2.5 shrink-0 font-mono text-xs">
            <div className="px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-800 flex items-center space-x-2">
              <Zap className="h-4 w-4 text-blue-400" />
              <span>Re-ID Engine: <strong className="text-blue-400">Multi-Feature Fusion</strong></span>
            </div>
            <div className="px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-800 flex items-center space-x-2">
              <Clock className="h-4 w-4 text-emerald-400" />
              <span>Re-ID Latency: <strong className="text-emerald-400">{matchResult?.reid_latency_ms || 0.4} ms</strong></span>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Switcher */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab('journey')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'journey'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20'
                : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>Multi-Camera Journey Simulator</span>
          </button>

          <button
            onClick={() => setActiveTab('matcher')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'matcher'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20'
                : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
            }`}
          >
            <Sliders className="w-4 h-4" />
            <span>Pairwise Re-ID Matcher Workbench</span>
          </button>
        </div>

        <span className="text-[10px] font-mono font-bold px-2.5 py-1 rounded bg-blue-500/10 text-blue-400 border border-blue-500/30">
          EXPLAINABLE RE-ID PROTOTYPE
        </span>
      </div>

      {demoError && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/60 text-rose-300 text-xs flex items-center gap-2.5">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{demoError}</span>
        </div>
      )}

      {/* TAB 1: Multi-Camera Journey Simulator */}
      {activeTab === 'journey' && (
        <div className="space-y-6">
          {/* Journey Header Card */}
          <div className="bg-[#0D1525] border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-emerald-400" />
                <h2 className="text-sm font-bold text-white">Pune Urban Corridor: Deccan &rarr; FC Road &rarr; Shivajinagar</h2>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Demonstrates uninterrupted tracking of vehicle <strong className="text-amber-400 font-mono">MH12AB1234</strong> across 3 cameras when plate readability is lost.
              </p>
            </div>

            <button
              onClick={loadDemoScenario}
              disabled={isLoadingDemo}
              className="flex items-center gap-2 px-3.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 rounded-lg text-xs font-semibold transition-colors shrink-0"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isLoadingDemo ? 'animate-spin' : ''}`} />
              <span>Rerun Journey Evaluation</span>
            </button>
          </div>

          {/* 3-Step Journey Timeline Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {demoData?.steps.map((step) => (
              <div
                key={step.step_number}
                className="bg-[#0D1525] border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between gap-4 relative overflow-hidden"
              >
                {/* Step Top Bar */}
                <div>
                  <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
                    <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 font-bold text-blue-400">
                      Camera {step.step_number} of 3
                    </span>
                    <span>{step.timestamp}</span>
                  </div>

                  <h3 className="text-sm font-bold text-white flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-blue-400" />
                    <span>{step.camera_name}</span>
                  </h3>
                  <span className="text-[11px] font-mono text-slate-500 block mb-3">{step.camera_id}</span>

                  {/* Vehicle & Plate Card */}
                  <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-2 font-mono text-xs">
                    <div className="flex justify-between items-center">
                      <span className="text-slate-400 text-[11px]">Plate Status:</span>
                      <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${
                        step.plate_status === 'READABLE'
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                          : 'bg-purple-500/10 text-purple-400 border-purple-500/30'
                      }`}>
                        {step.plate_status}
                      </span>
                    </div>

                    <div className="flex justify-between items-center">
                      <span className="text-slate-400 text-[11px]">Reading:</span>
                      <span className="font-bold text-amber-300">{step.plate_display}</span>
                    </div>

                    <div className="flex justify-between items-center">
                      <span className="text-slate-400 text-[11px]">Vehicle Body:</span>
                      <span className="text-slate-200">{step.vehicle_color} {step.vehicle_type}</span>
                    </div>
                  </div>
                </div>

                {/* Re-ID Match Result Section */}
                <div className="space-y-2 pt-2 border-t border-slate-800/80">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="text-slate-400">Match Score:</span>
                    <span className="font-extrabold text-base text-emerald-400">
                      {Math.round(step.match_score * 100)}%
                    </span>
                  </div>

                  <div className="h-1.5 bg-slate-900 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-emerald-500 rounded-full"
                      style={{ width: `${step.match_score * 100}%` }}
                    />
                  </div>

                  <span className={`inline-block text-[10px] font-mono font-semibold px-2 py-0.5 rounded border ${getClassificationBadge(step.match_classification)}`}>
                    {step.match_classification.replace(/_/g, ' ')}
                  </span>

                  {/* Evidence summary */}
                  <div className="pt-2 text-[11px] text-slate-400 space-y-1 font-sans">
                    {step.evidence_summary.map((ev, i) => (
                      <div key={i} className="flex items-start gap-1.5 text-[11px]">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                        <span className="text-slate-300">{ev}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Distractor Disambiguation Table */}
          <div className="bg-[#0D1525] border border-slate-800 rounded-xl p-5 shadow-lg space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-blue-400" />
                <span>Multi-Feature Disambiguation vs Distractor Vehicles</span>
              </h3>
              <span className="text-[10px] font-mono text-slate-400">
                Prevents false positives across co-occurring traffic
              </span>
            </div>

            <div className="overflow-x-auto rounded-lg border border-slate-800">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-900 text-[11px] uppercase tracking-wider text-slate-400 font-mono border-b border-slate-800">
                  <tr>
                    <th className="py-2.5 px-3.5">Candidate Vehicle</th>
                    <th className="py-2.5 px-3.5">Appearance Attributes</th>
                    <th className="py-2.5 px-3.5">Plate Number</th>
                    <th className="py-2.5 px-3.5">Similarity with Target</th>
                    <th className="py-2.5 px-3.5">Rejection Rationale</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-sans">
                  {demoData?.distractor_vehicles.map((d) => (
                    <tr key={d.vehicle_id} className="hover:bg-slate-900/50">
                      <td className="py-2.5 px-3.5 font-mono text-slate-200 font-semibold">
                        {d.vehicle_id}
                      </td>
                      <td className="py-2.5 px-3.5 font-semibold text-slate-300">
                        {d.color} {d.type}
                      </td>
                      <td className="py-2.5 px-3.5 font-mono text-amber-400">
                        {d.plate}
                      </td>
                      <td className="py-2.5 px-3.5 font-mono">
                        <span className="text-rose-400 font-bold">{Math.round(d.similarity_with_target * 100)}%</span>
                      </td>
                      <td className="py-2.5 px-3.5 text-slate-400 text-xs">
                        {d.rejection_reason}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: Interactive Pairwise Matcher Workbench */}
      {activeTab === 'matcher' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Input Signatures (6 cols) */}
          <div className="lg:col-span-6 space-y-4">
            {/* Source Vehicle */}
            <div className="bg-[#0D1525] border border-slate-800 rounded-xl p-5 shadow-lg space-y-3">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <span className="text-xs font-bold uppercase tracking-wider text-blue-400 flex items-center gap-2">
                  <Car className="w-4 h-4" />
                  <span>Source Observation (Camera A)</span>
                </span>
                <span className="text-[10px] font-mono text-slate-500">CAM_PUN_001</span>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <label className="text-slate-400 block mb-1 text-[11px]">Vehicle Color:</label>
                  <select
                    value={sourceColor}
                    onChange={(e) => setSourceColor(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-slate-200 text-xs focus:ring-0"
                  >
                    {['white', 'black', 'silver', 'grey', 'red', 'blue', 'green', 'yellow', 'orange', 'brown'].map((c) => (
                      <option key={c} value={c}>{c.toUpperCase()}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-slate-400 block mb-1 text-[11px]">Vehicle Type:</label>
                  <select
                    value={sourceType}
                    onChange={(e) => setSourceType(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-slate-200 text-xs focus:ring-0"
                  >
                    {['sedan', 'hatchback', 'suv', 'pickup', 'van', 'truck', 'motorcycle'].map((t) => (
                      <option key={t} value={t}>{t.toUpperCase()}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="space-y-1.5 pt-1">
                <label className="flex items-center justify-between text-[11px] text-slate-400">
                  <span>Plate Readable?</span>
                  <input
                    type="checkbox"
                    checked={sourcePlateReadable}
                    onChange={(e) => setSourcePlateReadable(e.target.checked)}
                    className="rounded bg-slate-900 text-blue-600 focus:ring-0"
                  />
                </label>
                {sourcePlateReadable && (
                  <input
                    type="text"
                    value={sourcePlate}
                    onChange={(e) => setSourcePlate(e.target.value)}
                    placeholder="e.g. MH12AB1234"
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 font-mono text-xs text-amber-300"
                  />
                )}
              </div>
            </div>

            {/* Target Vehicle */}
            <div className="bg-[#0D1525] border border-slate-800 rounded-xl p-5 shadow-lg space-y-3">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <span className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-2">
                  <Car className="w-4 h-4" />
                  <span>Candidate Observation (Camera B)</span>
                </span>
                <span className="text-[10px] font-mono text-slate-500">CAM_PUN_002 (+74s)</span>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <label className="text-slate-400 block mb-1 text-[11px]">Vehicle Color:</label>
                  <select
                    value={targetColor}
                    onChange={(e) => setTargetColor(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-slate-200 text-xs focus:ring-0"
                  >
                    {['white', 'black', 'silver', 'grey', 'red', 'blue', 'green', 'yellow', 'orange', 'brown'].map((c) => (
                      <option key={c} value={c}>{c.toUpperCase()}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-slate-400 block mb-1 text-[11px]">Vehicle Type:</label>
                  <select
                    value={targetType}
                    onChange={(e) => setTargetType(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-slate-200 text-xs focus:ring-0"
                  >
                    {['sedan', 'hatchback', 'suv', 'pickup', 'van', 'truck', 'motorcycle'].map((t) => (
                      <option key={t} value={t}>{t.toUpperCase()}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="space-y-1.5 pt-1">
                <label className="flex items-center justify-between text-[11px] text-slate-400">
                  <span>Plate Readable?</span>
                  <input
                    type="checkbox"
                    checked={targetPlateReadable}
                    onChange={(e) => setTargetPlateReadable(e.target.checked)}
                    className="rounded bg-slate-900 text-blue-600 focus:ring-0"
                  />
                </label>
                {targetPlateReadable ? (
                  <input
                    type="text"
                    value={targetPlate}
                    onChange={(e) => setTargetPlate(e.target.value)}
                    placeholder="e.g. MH12AB1234"
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 font-mono text-xs text-amber-300"
                  />
                ) : (
                  <p className="text-[11px] text-slate-500 font-mono italic">
                    Plate occluded / unreadable &rarr; Visual Re-ID fallback active
                  </p>
                )}
              </div>
            </div>

            <button
              onClick={executePairwiseMatch}
              disabled={isMatching}
              className="w-full flex items-center justify-center gap-2 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-blue-600/20 disabled:opacity-50 transition-all"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isMatching ? 'animate-spin' : ''}`} />
              <span>Calculate Re-ID Similarity</span>
            </button>
          </div>

          {/* Right Column: Live Match Results & Evidence (6 cols) */}
          <div className="lg:col-span-6 space-y-4">
            <div className="bg-[#0D1525] border border-slate-800 rounded-xl p-5 shadow-lg space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-amber-400" />
                  <span>Re-ID Match Result</span>
                </h3>
                <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${getClassificationBadge(matchResult?.classification || 'NO_MATCH')}`}>
                  {matchResult?.classification.replace(/_/g, ' ') || 'EVALUATING'}
                </span>
              </div>

              {/* Match Score Display */}
              <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-between">
                <div>
                  <span className="text-[10px] uppercase font-bold text-slate-400 block">Overall Similarity</span>
                  <span className="text-3xl font-extrabold text-emerald-400 font-mono">
                    {Math.round((matchResult?.overall_score || 0) * 100)}%
                  </span>
                </div>
                <div className="text-right text-xs font-mono">
                  <span className="text-slate-500 block text-[10px] uppercase">Method</span>
                  <span className="text-blue-400 font-bold">{matchResult?.method_used}</span>
                </div>
              </div>

              {/* Feature-Level Score Breakdown Bars */}
              <div className="space-y-2.5 text-xs font-sans">
                <div>
                  <div className="flex justify-between text-[11px] text-slate-400 mb-1 font-mono">
                    <span>Vehicle Color Match</span>
                    <span>{Math.round((matchResult?.evidence.color_similarity || 0) * 100)}%</span>
                  </div>
                  <div className="h-1.5 bg-slate-900 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-500 rounded-full"
                      style={{ width: `${(matchResult?.evidence.color_similarity || 0) * 100}%` }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-[11px] text-slate-400 mb-1 font-mono">
                    <span>Vehicle Type &amp; Geometry</span>
                    <span>{Math.round((matchResult?.evidence.type_similarity || 0) * 100)}%</span>
                  </div>
                  <div className="h-1.5 bg-slate-900 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-cyan-500 rounded-full"
                      style={{ width: `${(matchResult?.evidence.type_similarity || 0) * 100}%` }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-[11px] text-slate-400 mb-1 font-mono">
                    <span>Visual Appearance &amp; Texture</span>
                    <span>{Math.round((matchResult?.evidence.appearance_similarity || 0) * 100)}%</span>
                  </div>
                  <div className="h-1.5 bg-slate-900 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-emerald-500 rounded-full"
                      style={{ width: `${(matchResult?.evidence.appearance_similarity || 0) * 100}%` }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-[11px] text-slate-400 mb-1 font-mono">
                    <span>Silhouette Aspect Ratio</span>
                    <span>{Math.round((matchResult?.evidence.shape_similarity || 0) * 100)}%</span>
                  </div>
                  <div className="h-1.5 bg-slate-900 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-amber-500 rounded-full"
                      style={{ width: `${(matchResult?.evidence.shape_similarity || 0) * 100}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Natural Language Explanation Box */}
              <div className="p-3.5 bg-slate-950 rounded-lg border border-slate-800 font-mono text-[11px] text-slate-300 whitespace-pre-wrap leading-relaxed">
                {matchResult?.explanation || 'Computing feature evidence...'}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
