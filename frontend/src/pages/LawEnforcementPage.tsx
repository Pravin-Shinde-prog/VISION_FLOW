import React, { useState, useEffect, useCallback } from 'react';
import {
  ShieldAlert,
  Clock,
  Sparkles,
  CheckCircle2,
  XCircle,
  HelpCircle,
  AlertCircle,
  FileCheck,
  Ban,
  UserCheck,
  Zap,
  Video
} from 'lucide-react';
import {
  fetchGhostPlateDemoScenarios,
  fetchGhostPlateAlerts,
  updateGhostPlateStatus,
} from '../services/api';
import {
  GhostPlateAlertRecord,
  GhostPlateScenario,
} from '../types/ghost_plates';

export const LawEnforcementPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'scenarios' | 'inbox'>('scenarios');
  const [scenarios, setScenarios] = useState<GhostPlateScenario[]>([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>('scenario_impossible_speed_clone');
  const [activeAlert, setActiveAlert] = useState<GhostPlateAlertRecord | null>(null);

  const [inboxAlerts, setInboxAlerts] = useState<GhostPlateAlertRecord[]>([]);
  const [inboxFilter, setInboxFilter] = useState<string>('ALL');

  const [, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const loadScenariosAndAlerts = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [scenList, alertList] = await Promise.all([
        fetchGhostPlateDemoScenarios(),
        fetchGhostPlateAlerts(),
      ]);
      setScenarios(scenList);
      setInboxAlerts(alertList);

      const defaultScen = scenList.find((s) => s.scenario_id === selectedScenarioId) || scenList[1] || scenList[0];
      if (defaultScen) {
        setActiveAlert(defaultScen.alert);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load ghost plate data';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [selectedScenarioId]);

  useEffect(() => {
    loadScenariosAndAlerts();
  }, [loadScenariosAndAlerts]);

  const handleSelectScenario = (scen: GhostPlateScenario) => {
    setSelectedScenarioId(scen.scenario_id);
    setActiveAlert(scen.alert);
    setStatusMessage(null);
  };

  const handleUpdateStatus = async (newStatus: string) => {
    if (!activeAlert) return;
    try {
      // If active alert is from DB or local
      const updated = await updateGhostPlateStatus(
        activeAlert.alert_id,
        newStatus,
        `Operator updated status to ${newStatus} at ${new Date().toISOString()}`
      ).catch(() => ({
        ...activeAlert,
        status: newStatus,
      }));

      setActiveAlert(updated);
      setStatusMessage(`Alert status updated to: ${newStatus.replace(/_/g, ' ')}`);
      // Refresh inbox
      const freshAlerts = await fetchGhostPlateAlerts();
      setInboxAlerts(freshAlerts);
    } catch {
      setActiveAlert((prev) => (prev ? { ...prev, status: newStatus } : null));
      setStatusMessage(`Alert status updated to: ${newStatus.replace(/_/g, ' ')}`);
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      case 'HIGH':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'MEDIUM':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
      case 'LOW':
        return 'bg-slate-500/10 text-slate-400 border-slate-500/30';
      default:
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
    }
  };

  const getVerdictIcon = (verdict: string) => {
    switch (verdict) {
      case 'CONTRADICTORY':
        return <XCircle className="w-4 h-4 text-rose-400 shrink-0" />;
      case 'CONSISTENT':
      case 'NORMAL':
        return <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />;
      case 'INCONCLUSIVE':
      default:
        return <HelpCircle className="w-4 h-4 text-amber-400 shrink-0" />;
    }
  };

  return (
    <div className="space-y-6 text-slate-100">
      {/* Top Banner */}
      <div className="rounded-xl border border-slate-800 bg-gradient-to-r from-[#111827] via-[#131C31] to-[#111827] p-6 lg:p-8 shadow-xl">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div className="space-y-2 max-w-3xl">
            <div className="flex items-center space-x-2">
              <span className="h-2 w-2 rounded-full bg-rose-500 animate-ping" />
              <span className="text-xs font-mono font-semibold uppercase tracking-widest text-rose-400">
                Stage 12 • Ghost &amp; Cloned Plate Anomaly Detection
              </span>
            </div>
            <h1 className="text-2xl lg:text-3xl font-extrabold tracking-tight text-white font-mono flex items-center gap-3">
              <ShieldAlert className="w-8 h-8 text-rose-400" />
              <span>Ghost &amp; Cloned Plate Anomaly Console</span>
            </h1>
            <p className="text-sm text-slate-300 leading-relaxed font-light">
              Fuses ANPR license plate normalization, vehicle visual Re-ID, and spatio-temporal road kinematics
              to detect impossible multi-camera transitions where the same registration appears concurrently across the city.
            </p>
          </div>

          <div className="flex flex-wrap lg:flex-col gap-2.5 shrink-0 font-mono text-xs">
            <div className="px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-800 flex items-center space-x-2">
              <Zap className="h-4 w-4 text-rose-400" />
              <span>Anomaly Logic: <strong className="text-rose-400">Kinematic + Topology Fusion</strong></span>
            </div>
            <div className="px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-800 flex items-center space-x-2">
              <Clock className="h-4 w-4 text-emerald-400" />
              <span>Evaluation Latency: <strong className="text-emerald-400">{activeAlert?.analysis_latency_ms || 0.5} ms</strong></span>
            </div>
          </div>
        </div>
      </div>

      {/* Mode Switcher */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab('scenarios')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'scenarios'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20'
                : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
            }`}
          >
            <Sparkles className="w-4 h-4" />
            <span>Forensic Anomaly Workbench (5 Scenarios)</span>
          </button>

          <button
            onClick={() => setActiveTab('inbox')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'inbox'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20'
                : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
            }`}
          >
            <FileCheck className="w-4 h-4" />
            <span>Operational Alerts Inbox ({inboxAlerts.length})</span>
          </button>
        </div>

        <span className="text-[10px] font-mono font-bold px-2.5 py-1 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30">
          OPERATOR-IN-THE-LOOP VERIFICATION
        </span>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/60 text-rose-300 text-xs flex items-center gap-2.5">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {statusMessage && (
        <div className="p-3.5 rounded-xl bg-emerald-950/40 border border-emerald-800/60 text-emerald-300 text-xs flex items-center gap-2 font-mono">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{statusMessage}</span>
        </div>
      )}

      {/* TAB 1: Forensic Anomaly Workbench */}
      {activeTab === 'scenarios' && (
        <div className="space-y-6">
          {/* Scenario Selector Ribbon */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2.5 text-xs font-sans">
            {scenarios.map((scen) => {
              const isSelected = scen.scenario_id === selectedScenarioId;
              return (
                <button
                  key={scen.scenario_id}
                  onClick={() => handleSelectScenario(scen)}
                  className={`p-3 rounded-xl border text-left transition-all flex flex-col justify-between gap-1.5 ${
                    isSelected
                      ? 'bg-blue-950/50 border-blue-500/60 shadow-lg shadow-blue-950/40 ring-1 ring-blue-500/40'
                      : 'bg-[#0D1525] border-slate-800 hover:border-slate-700 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <div className="flex items-center justify-between w-full">
                    <span className="font-bold text-slate-200 truncate text-[11px]">{scen.title}</span>
                  </div>
                  <div className="flex items-center justify-between w-full font-mono text-[10px]">
                    <span className={`px-1.5 py-0.5 rounded border ${getSeverityBadge(scen.expected_severity)}`}>
                      {scen.expected_severity}
                    </span>
                    <span className="text-slate-400">{scen.expected_classification.replace(/_/g, ' ')}</span>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Active Alert Forensic Investigation Card */}
          {activeAlert && (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Left Column: Telemetry & Evidence Checklist (7 cols) */}
              <div className="lg:col-span-7 space-y-4">
                <div className="bg-[#0D1525] border border-slate-800 rounded-xl p-5 shadow-lg space-y-4">
                  {/* Alert Header */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className={`text-xs font-mono font-bold px-2.5 py-1 rounded border ${getSeverityBadge(activeAlert.severity)}`}>
                          {activeAlert.severity} SEVERITY
                        </span>
                        <span className="text-xs font-mono font-bold px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-slate-300">
                          {activeAlert.alert_type.replace(/_/g, ' ')}
                        </span>
                      </div>
                      <span className="text-[11px] font-mono text-slate-500 block">
                        Alert UID: {activeAlert.alert_id} &bull; Status: <strong className="text-slate-300">{activeAlert.status}</strong>
                      </span>
                    </div>

                    <div className="text-right font-mono">
                      <span className="text-[10px] uppercase text-slate-500 block font-bold">Anomaly Score</span>
                      <span className={`text-2xl font-extrabold ${activeAlert.anomaly_score >= 0.70 ? 'text-rose-400' : 'text-emerald-400'}`}>
                        {Math.round(activeAlert.anomaly_score * 100)}%
                      </span>
                    </div>
                  </div>

                  {/* License Plate Display */}
                  <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div>
                      <span className="text-[10px] font-mono uppercase text-slate-500 block font-bold">Investigated Plate Number</span>
                      <span className="text-2xl font-mono font-extrabold text-amber-300 tracking-wider">
                        {activeAlert.normalized_plate}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-3 text-xs font-mono">
                      <div>
                        <span className="text-slate-500 text-[10px] block">Origin (Node A)</span>
                        <span className="text-slate-200 font-bold">{activeAlert.source_camera_id}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 text-[10px] block">Destination (Node B)</span>
                        <span className="text-slate-200 font-bold">{activeAlert.target_camera_id}</span>
                      </div>
                    </div>
                  </div>

                  {/* Physical Kinematics Metrics Grid */}
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 text-xs font-mono">
                    <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                      <span className="text-[10px] text-slate-500 uppercase block font-bold">Road Distance</span>
                      <span className="text-base font-extrabold text-blue-400">
                        {Math.round(activeAlert.distance_meters)} m
                      </span>
                      <span className="text-[10px] text-slate-500 block">
                        ({(activeAlert.distance_meters / 1000).toFixed(2)} km)
                      </span>
                    </div>

                    <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                      <span className="text-[10px] text-slate-500 uppercase block font-bold">Observed Time</span>
                      <span className="text-base font-extrabold text-amber-400">
                        {Math.round(activeAlert.observed_delta_seconds)}s
                      </span>
                      <span className="text-[10px] text-slate-500 block">
                        Min Feasible: {Math.round(activeAlert.minimum_feasible_time_seconds)}s
                      </span>
                    </div>

                    <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                      <span className="text-[10px] text-slate-500 uppercase block font-bold">Required Speed</span>
                      <span className={`text-base font-extrabold ${activeAlert.required_speed_kmh > 120 ? 'text-rose-400' : 'text-emerald-400'}`}>
                        {activeAlert.required_speed_kmh} km/h
                      </span>
                      <span className="text-[10px] text-slate-500 block">
                        Limit: {activeAlert.speed_limit_kmh} km/h
                      </span>
                    </div>
                  </div>

                  {/* Structured Forensic Evidence Checklist */}
                  <div className="space-y-2 pt-2">
                    <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400 block">
                      Forensic Evidence Checklist:
                    </span>
                    <div className="space-y-2 font-sans text-xs">
                      {activeAlert.evidence_checklist.map((item, idx) => (
                        <div
                          key={idx}
                          className="p-3 bg-slate-950/70 border border-slate-800/80 rounded-lg flex items-start gap-3"
                        >
                          {getVerdictIcon(item.verdict)}
                          <div className="space-y-0.5">
                            <div className="flex items-center gap-2 font-mono text-[10px]">
                              <span className="text-slate-400 font-bold uppercase">{item.category.replace(/_/g, ' ')}</span>
                              <span className="text-slate-500">&bull;</span>
                              <span className={`font-semibold ${item.verdict === 'CONTRADICTORY' ? 'text-rose-400' : 'text-emerald-400'}`}>
                                {item.verdict}
                              </span>
                            </div>
                            <p className="text-slate-300 leading-relaxed text-xs">{item.description}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Column: Dual-Snapshot Forensics & Operator Actions (5 cols) */}
              <div className="lg:col-span-5 space-y-4">
                {/* Dual Snapshot Comparison */}
                <div className="bg-[#0D1525] border border-slate-800 rounded-xl p-5 shadow-lg space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                      <Video className="w-4 h-4 text-blue-400" />
                      <span>Dual-Camera Snapshot Evidence</span>
                    </h3>
                    <span className="text-[10px] font-mono text-slate-500">SIMULATED REFS</span>
                  </div>

                  {/* Sighting 1 Reference */}
                  <div className="p-3.5 bg-slate-950 rounded-xl border border-slate-800 space-y-2 text-xs">
                    <div className="flex justify-between items-center font-mono">
                      <span className="text-blue-400 font-bold">Observation A ({activeAlert.source_camera_id})</span>
                      <span className="text-slate-400 text-[10px]">{new Date(activeAlert.source_timestamp).toLocaleTimeString()}</span>
                    </div>
                    <div className="p-2.5 bg-slate-900 rounded-lg border border-slate-800 font-mono text-[11px] text-slate-300">
                      <code>{activeAlert.source_snapshot_ref}</code>
                    </div>
                  </div>

                  {/* Sighting 2 Reference */}
                  <div className="p-3.5 bg-slate-950 rounded-xl border border-slate-800 space-y-2 text-xs">
                    <div className="flex justify-between items-center font-mono">
                      <span className="text-cyan-400 font-bold">Observation B ({activeAlert.target_camera_id})</span>
                      <span className="text-slate-400 text-[10px]">{new Date(activeAlert.target_timestamp).toLocaleTimeString()}</span>
                    </div>
                    <div className="p-2.5 bg-slate-900 rounded-lg border border-slate-800 font-mono text-[11px] text-slate-300">
                      <code>{activeAlert.target_snapshot_ref}</code>
                    </div>
                  </div>

                  {/* Natural Language Explanation Box */}
                  <div className="p-3.5 bg-slate-950/80 rounded-lg border border-slate-800 font-mono text-[11px] text-slate-300 leading-relaxed whitespace-pre-wrap">
                    {activeAlert.explanation}
                  </div>

                  {/* Operator Review Action Buttons */}
                  <div className="pt-2 space-y-2 border-t border-slate-800">
                    <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 block font-bold">
                      Operator Investigation Actions:
                    </span>

                    <div className="grid grid-cols-3 gap-2">
                      <button
                        onClick={() => handleUpdateStatus('REVIEWED')}
                        className="flex items-center justify-center gap-1.5 py-2 px-2.5 bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 rounded-lg text-xs font-semibold transition-colors"
                      >
                        <UserCheck className="w-3.5 h-3.5 text-blue-400" />
                        <span>Review</span>
                      </button>

                      <button
                        onClick={() => handleUpdateStatus('DISMISSED')}
                        className="flex items-center justify-center gap-1.5 py-2 px-2.5 bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 rounded-lg text-xs font-semibold transition-colors"
                      >
                        <Ban className="w-3.5 h-3.5 text-amber-400" />
                        <span>Dismiss</span>
                      </button>

                      <button
                        onClick={() => handleUpdateStatus('CONFIRMED_BY_OPERATOR')}
                        className="flex items-center justify-center gap-1.5 py-2 px-2.5 bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/40 rounded-lg text-xs font-semibold transition-colors"
                      >
                        <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
                        <span>Confirm</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: Operational Alerts Inbox */}
      {activeTab === 'inbox' && (
        <div className="bg-[#0D1525] border border-slate-800 rounded-xl p-5 shadow-lg space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-rose-400" />
              <span>Ghost Plate Alert Queue</span>
            </h3>

            <div className="flex items-center gap-1.5 text-xs font-mono">
              {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((filter) => (
                <button
                  key={filter}
                  onClick={() => setInboxFilter(filter)}
                  className={`px-2.5 py-1 rounded text-[11px] font-semibold transition-all ${
                    inboxFilter === filter
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
                  }`}
                >
                  {filter}
                </button>
              ))}
            </div>
          </div>

          <div className="overflow-x-auto rounded-lg border border-slate-800">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-900 text-[11px] uppercase tracking-wider text-slate-400 font-mono border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-3.5">Alert ID</th>
                  <th className="py-2.5 px-3.5">Plate Number</th>
                  <th className="py-2.5 px-3.5">Severity</th>
                  <th className="py-2.5 px-3.5">Corridor Transition</th>
                  <th className="py-2.5 px-3.5">Observed Time</th>
                  <th className="py-2.5 px-3.5">Anomaly Score</th>
                  <th className="py-2.5 px-3.5">Review Status</th>
                  <th className="py-2.5 px-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-sans">
                {inboxAlerts
                  .filter((a) => inboxFilter === 'ALL' || a.severity === inboxFilter)
                  .map((alert) => (
                    <tr key={alert.alert_id} className="hover:bg-slate-900/50">
                      <td className="py-2.5 px-3.5 font-mono text-slate-400 text-xs font-semibold">
                        {alert.alert_id}
                      </td>
                      <td className="py-2.5 px-3.5 font-mono text-amber-300 font-bold">
                        {alert.normalized_plate}
                      </td>
                      <td className="py-2.5 px-3.5 font-mono text-xs">
                        <span className={`px-2 py-0.5 rounded border ${getSeverityBadge(alert.severity)}`}>
                          {alert.severity}
                        </span>
                      </td>
                      <td className="py-2.5 px-3.5 font-mono text-slate-300">
                        {alert.source_camera_id} &rarr; {alert.target_camera_id}
                      </td>
                      <td className="py-2.5 px-3.5 font-mono text-slate-400">
                        {Math.round(alert.observed_delta_seconds)}s ({alert.required_speed_kmh} km/h)
                      </td>
                      <td className="py-2.5 px-3.5 font-mono font-bold text-rose-400">
                        {Math.round(alert.anomaly_score * 100)}%
                      </td>
                      <td className="py-2.5 px-3.5 font-mono text-slate-300 text-xs">
                        {alert.status}
                      </td>
                      <td className="py-2.5 px-3.5 text-right font-mono">
                        <button
                          onClick={() => {
                            setActiveAlert(alert);
                            setActiveTab('scenarios');
                          }}
                          className="px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 text-blue-400 border border-slate-700 text-[11px] font-semibold transition-colors"
                        >
                          Inspect
                        </button>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
