import React, { useState, useEffect, useCallback } from 'react';
import {
  Play,
  Trash2,
  Cpu,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  Car,
  Hash,
  Layers,
  Sparkles
} from 'lucide-react';
import { runSimulation, getSimulationStatus, cleanupSimulation } from '../../services/api';
import { SimulationStatusResponse } from '../../types/simulation';

interface SimulationControlCardProps {
  onSimulationCompleted?: () => void;
}

export const SimulationControlCard: React.FC<SimulationControlCardProps> = ({
  onSimulationCompleted,
}) => {
  // Config inputs
  const [vehicleCount, setVehicleCount] = useState<number>(30);
  const [eventsPerVehicle, setEventsPerVehicle] = useState<number>(5);
  const [seed, setSeed] = useState<number>(42);

  // Status & execution state
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [isCleaning, setIsCleaning] = useState<boolean>(false);
  const [status, setStatus] = useState<SimulationStatusResponse | null>(null);
  const [feedbackMessage, setFeedbackMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  const loadStatus = useCallback(async () => {
    try {
      const res = await getSimulationStatus();
      setStatus(res);
    } catch {
      // Non-critical telemetry fetch
    }
  }, []);

  useEffect(() => {
    loadStatus();
  }, [loadStatus]);

  const handleRunSimulation = async () => {
    setIsRunning(true);
    setFeedbackMessage(null);
    try {
      const res = await runSimulation({
        vehicle_count: vehicleCount,
        events_per_vehicle: eventsPerVehicle,
        seed: seed,
      });
      setFeedbackMessage({
        text: `Successfully generated ${res.vehicles_created} vehicles and ${res.events_created} camera sightings in ${res.duration_seconds}s (Seed: ${res.seed}).`,
        type: 'success',
      });
      await loadStatus();
      onSimulationCompleted?.();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Simulation run failed';
      setFeedbackMessage({ text: msg, type: 'error' });
    } finally {
      setIsRunning(false);
    }
  };

  const handleCleanup = async () => {
    if (!window.confirm('Purge all simulated vehicles and detection sightings from the database?')) {
      return;
    }

    setIsCleaning(true);
    setFeedbackMessage(null);
    try {
      const res = await cleanupSimulation();
      setFeedbackMessage({
        text: `Cleaned ${res.detections_deleted} detections, ${res.plates_deleted} plates, and ${res.vehicles_deleted} vehicles.`,
        type: 'success',
      });
      await loadStatus();
      onSimulationCompleted?.();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Cleanup failed';
      setFeedbackMessage({ text: msg, type: 'error' });
    } finally {
      setIsCleaning(false);
    }
  };

  return (
    <div className="bg-[#0D1525] border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col gap-4 text-slate-100">
      {/* Card Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-blue-600/20 text-blue-400 rounded-lg border border-blue-500/30">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-white">Synthetic Traffic & Event Generator</h2>
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/30">
                SIMULATED DATA ADAPTER
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Simulates realistic vehicle movement through the Pune directed camera graph for prototype demonstrations.
            </p>
          </div>
        </div>

        {/* Live Telemetry Badges */}
        <div className="flex items-center gap-2 font-mono text-xs">
          <div className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
            <span className="text-slate-500 mr-1">Vehicles:</span>
            <span className="font-bold text-blue-400">{status?.total_simulated_vehicles || 0}</span>
          </div>
          <div className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
            <span className="text-slate-500 mr-1">Sightings:</span>
            <span className="font-bold text-cyan-400">{status?.total_simulated_events || 0}</span>
          </div>
        </div>
      </div>

      {/* Parameter Controls Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
        {/* Vehicle Count */}
        <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800 flex flex-col gap-1.5">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400 flex items-center gap-1">
              <Car className="w-3.5 h-3.5 text-blue-400" />
              Fleet Size (Vehicles)
            </span>
            <span className="font-mono font-bold text-blue-400">{vehicleCount}</span>
          </div>
          <input
            type="range"
            min="5"
            max="100"
            step="5"
            value={vehicleCount}
            onChange={(e) => setVehicleCount(parseInt(e.target.value, 10))}
            className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
          />
          <div className="flex justify-between text-[10px] text-slate-500 font-mono">
            <span>5</span>
            <span>30 (Default)</span>
            <span>100</span>
          </div>
        </div>

        {/* Sightings per vehicle */}
        <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800 flex flex-col gap-1.5">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400 flex items-center gap-1">
              <Layers className="w-3.5 h-3.5 text-cyan-400" />
              Sightings / Vehicle
            </span>
            <span className="font-mono font-bold text-cyan-400">{eventsPerVehicle}</span>
          </div>
          <input
            type="range"
            min="2"
            max="12"
            step="1"
            value={eventsPerVehicle}
            onChange={(e) => setEventsPerVehicle(parseInt(e.target.value, 10))}
            className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
          />
          <div className="flex justify-between text-[10px] text-slate-500 font-mono">
            <span>2</span>
            <span>5 (Default)</span>
            <span>12</span>
          </div>
        </div>

        {/* Deterministic Seed */}
        <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800 flex flex-col gap-1.5">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400 flex items-center gap-1">
              <Hash className="w-3.5 h-3.5 text-amber-400" />
              Random Seed (Reproducibility)
            </span>
            <button
              onClick={() => setSeed(Math.floor(Math.random() * 10000))}
              className="text-[10px] text-amber-400 hover:text-amber-300 font-mono"
            >
              Randomize
            </button>
          </div>
          <input
            type="number"
            value={seed}
            onChange={(e) => setSeed(parseInt(e.target.value || '0', 10))}
            className="w-full px-2.5 py-1 bg-slate-950 border border-slate-700 rounded text-xs font-mono text-slate-200 focus:outline-none focus:border-amber-500"
          />
          <span className="text-[10px] text-slate-500">Seed 42 generates standard SIH demonstration scenario</span>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
        <div className="flex items-center gap-2">
          <button
            onClick={handleRunSimulation}
            disabled={isRunning || isCleaning}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow-lg shadow-blue-600/20 disabled:opacity-50 transition-all"
          >
            {isRunning ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Play className="w-4 h-4 fill-current" />
            )}
            <span>{isRunning ? 'Simulating Traffic...' : 'Run Simulation Scenario'}</span>
          </button>

          <button
            onClick={handleCleanup}
            disabled={isRunning || isCleaning || !status || status.total_simulated_vehicles === 0}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-slate-900 hover:bg-rose-950/40 text-rose-400 hover:text-rose-300 border border-slate-800 hover:border-rose-500/40 rounded-lg text-xs font-semibold disabled:opacity-30 transition-all"
            title="Delete all synthetic simulation records"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>{isCleaning ? 'Purging...' : 'Purge Simulation Data'}</span>
          </button>
        </div>

        <div className="text-xs text-slate-400 font-mono flex items-center gap-1">
          <Sparkles className="w-3.5 h-3.5 text-blue-400" />
          <span>Graph-Constrained Road Routing</span>
        </div>
      </div>

      {/* Feedback Banner */}
      {feedbackMessage && (
        <div
          className={`p-3 rounded-lg text-xs flex items-center gap-2.5 ${
            feedbackMessage.type === 'success'
              ? 'bg-emerald-950/30 border border-emerald-700/40 text-emerald-300'
              : 'bg-rose-950/30 border border-rose-700/40 text-rose-300'
          }`}
        >
          {feedbackMessage.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          ) : (
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          )}
          <span>{feedbackMessage.text}</span>
        </div>
      )}
    </div>
  );
};
