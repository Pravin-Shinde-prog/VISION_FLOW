import React, { useState, useEffect, useCallback } from 'react';
import {
  GitFork,
  Clock,
  Sparkles,
  ArrowRight,
  AlertCircle,
  Layers,
  Activity,
  Compass
} from 'lucide-react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import L from 'leaflet';
import {
  fetchGraphTopology,
  findDirectedPath,
  validateGraphTransition,
  fetchGraphDemoScenarios,
} from '../services/api';
import {
  GraphTopologyResponse,
  GraphPathResponse,
  TransitionValidationResponse,
  GraphDemoScenario,
} from '../types/graph';

// Custom Map Marker Icons
const defaultMarkerIcon = L.divIcon({
  className: 'custom-camera-pin',
  html: `<div style="background-color: #3b82f6; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 6px rgba(0,0,0,0.5);"></div>`,
  iconSize: [12, 12],
  iconAnchor: [6, 6],
});

const activeMarkerIcon = L.divIcon({
  className: 'custom-active-camera-pin',
  html: `<div style="background-color: #10b981; width: 16px; height: 16px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 10px #10b981;"></div>`,
  iconSize: [16, 16],
  iconAnchor: [8, 8],
});

export const TrajectoryEnginePage: React.FC = () => {
  const [topology, setTopology] = useState<GraphTopologyResponse | null>(null);
  const [activeTab, setActiveTab] = useState<'validator' | 'scenarios'>('validator');
  const [demoScenarios, setDemoScenarios] = useState<GraphDemoScenario[]>([]);

  // Selection state
  const [sourceCamera, setSourceCamera] = useState<string>('CAM_PUN_001');
  const [targetCamera, setTargetCamera] = useState<string>('CAM_PUN_004');
  const [observedDeltaSec, setObservedDeltaSec] = useState<number>(180);
  const [congestionTolerance, setCongestionTolerance] = useState<number>(3.5);

  const [pathResult, setPathResult] = useState<GraphPathResponse | null>(null);
  const [validationResult, setValidationResult] = useState<TransitionValidationResponse | null>(null);
  const [, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const loadInitialData = useCallback(async () => {
    try {
      const [topData, scenData] = await Promise.all([
        fetchGraphTopology(),
        fetchGraphDemoScenarios(),
      ]);
      setTopology(topData);
      setDemoScenarios(scenData);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load graph data';
      setError(msg);
    }
  }, []);

  const executePathSearchAndValidation = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const baseTime = new Date('2026-08-27T10:00:00Z');
      const targetTime = new Date(baseTime.getTime() + observedDeltaSec * 1000);

      const [path, validation] = await Promise.all([
        findDirectedPath(sourceCamera, targetCamera),
        validateGraphTransition({
          source_camera_id: sourceCamera,
          target_camera_id: targetCamera,
          source_timestamp: baseTime.toISOString(),
          target_timestamp: targetTime.toISOString(),
          plate_number: 'MH12AB1234',
          reid_confidence: 0.92,
          congestion_tolerance_factor: congestionTolerance,
        }),
      ]);

      setPathResult(path);
      setValidationResult(validation);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Validation failed';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [sourceCamera, targetCamera, observedDeltaSec, congestionTolerance]);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  useEffect(() => {
    executePathSearchAndValidation();
  }, [executePathSearchAndValidation]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'TEMPORALLY_FEASIBLE':
      case 'SAME_LOCATION_STATIONARY':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'TOO_FAST':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      case 'TOO_SLOW':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'NO_FEASIBLE_PATH':
      default:
        return 'bg-purple-500/10 text-purple-400 border-purple-500/30';
    }
  };

  // Extract path polyline coordinates for Leaflet
  const getActivePathCoordinates = (): [number, number][] => {
    if (!pathResult || !pathResult.path_exists || !topology) return [];
    const nodeMap = new Map(topology.nodes.map((n) => [n.camera_id, n]));
    const coords: [number, number][] = [];
    for (const cid of pathResult.camera_path) {
      const node = nodeMap.get(cid);
      if (node) coords.push([node.latitude, node.longitude]);
    }
    return coords;
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
                Stage 11 • Spatio-Temporal Graph Engine
              </span>
            </div>
            <h1 className="text-2xl lg:text-3xl font-extrabold tracking-tight text-white font-mono flex items-center gap-3">
              <GitFork className="w-8 h-8 text-blue-400" />
              <span>Spatio-Temporal Directed Road Graph G=(V,E)</span>
            </h1>
            <p className="text-sm text-slate-300 leading-relaxed font-light">
              Directed weighted road network modeling camera station topologies, shortest path Dijkstra routing,
              and physical travel time kinematics to validate forward vehicle feasibility.
            </p>
          </div>

          <div className="flex flex-wrap lg:flex-col gap-2.5 shrink-0 font-mono text-xs">
            <div className="px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-800 flex items-center space-x-2">
              <Layers className="h-4 w-4 text-blue-400" />
              <span>Network: <strong className="text-blue-400">15 Nodes • 17 Edges</strong></span>
            </div>
            <div className="px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-800 flex items-center space-x-2">
              <Clock className="h-4 w-4 text-emerald-400" />
              <span>Latency: <strong className="text-emerald-400">{validationResult?.validation_latency_ms || 0.5} ms</strong></span>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Switcher */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab('validator')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'validator'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20'
                : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
            }`}
          >
            <Compass className="w-4 h-4" />
            <span>Interactive Route Validator</span>
          </button>

          <button
            onClick={() => setActiveTab('scenarios')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'scenarios'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20'
                : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
            }`}
          >
            <Sparkles className="w-4 h-4" />
            <span>Demonstration Scenarios</span>
          </button>
        </div>

        <span className="text-[10px] font-mono font-bold px-2.5 py-1 rounded bg-blue-500/10 text-blue-400 border border-blue-500/30">
          PHYSICAL KINEMATICS ENGINE
        </span>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/60 text-rose-300 text-xs flex items-center gap-2.5">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* TAB 1: Interactive Route Validator */}
      {activeTab === 'validator' && (
        <div className="space-y-6">
          {/* Controls Bar */}
          <div className="bg-[#0D1525] border border-slate-800 rounded-xl p-4 shadow-lg grid grid-cols-1 md:grid-cols-4 gap-4 text-xs">
            {/* Source Camera */}
            <div>
              <label className="text-slate-400 block mb-1 font-mono text-[11px]">Origin Camera (Node A):</label>
              <select
                value={sourceCamera}
                onChange={(e) => setSourceCamera(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-slate-200 text-xs font-mono focus:ring-0"
              >
                {topology?.nodes.map((n) => (
                  <option key={n.camera_id} value={n.camera_id}>
                    {n.camera_id} — {n.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Target Camera */}
            <div>
              <label className="text-slate-400 block mb-1 font-mono text-[11px]">Destination Camera (Node B):</label>
              <select
                value={targetCamera}
                onChange={(e) => setTargetCamera(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-slate-200 text-xs font-mono focus:ring-0"
              >
                {topology?.nodes.map((n) => (
                  <option key={n.camera_id} value={n.camera_id}>
                    {n.camera_id} — {n.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Observed Delta Time */}
            <div>
              <label className="text-slate-400 block mb-1 font-mono text-[11px]">
                Observed Travel Time: <strong className="text-amber-400">{observedDeltaSec}s ({Math.round(observedDeltaSec/60)} min)</strong>
              </label>
              <input
                type="range"
                min="5"
                max="1800"
                step="5"
                value={observedDeltaSec}
                onChange={(e) => setObservedDeltaSec(parseInt(e.target.value))}
                className="w-full h-1 bg-slate-800 rounded accent-blue-500 mt-2"
              />
            </div>

            {/* Congestion Multiplier */}
            <div>
              <label className="text-slate-400 block mb-1 font-mono text-[11px]">
                Congestion Tolerance: <strong className="text-cyan-400">{congestionTolerance.toFixed(1)}x</strong>
              </label>
              <input
                type="range"
                min="1.0"
                max="6.0"
                step="0.5"
                value={congestionTolerance}
                onChange={(e) => setCongestionTolerance(parseFloat(e.target.value))}
                className="w-full h-1 bg-slate-800 rounded accent-cyan-500 mt-2"
              />
            </div>
          </div>

          {/* Main Visual & Telemetry Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Column: GIS Map & Directed Topology (7 cols) */}
            <div className="lg:col-span-7 bg-[#0D1525] border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col gap-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <Compass className="w-4 h-4 text-blue-400" />
                  <h2 className="text-sm font-bold text-white">Pune Road Network GIS &amp; Path Traversal</h2>
                </div>

                <span className="text-[11px] font-mono text-slate-400">
                  {pathResult?.path_exists ? `${pathResult.hop_count} Directed Hop(s)` : 'No Path'}
                </span>
              </div>

              {/* Leaflet Map Canvas */}
              <div className="relative rounded-lg overflow-hidden bg-slate-950 border border-slate-800 h-[380px]">
                <MapContainer
                  center={[18.524, 73.845]}
                  zoom={13}
                  className="w-full h-full"
                >
                  <TileLayer
                    url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                    attribution='&copy; <a href="https://carto.com/">CARTO</a>'
                  />

                  {/* Render All Camera Nodes */}
                  {topology?.nodes.map((node) => {
                    const isPathNode = pathResult?.camera_path.includes(node.camera_id);
                    return (
                      <Marker
                        key={node.camera_id}
                        position={[node.latitude, node.longitude]}
                        icon={isPathNode ? activeMarkerIcon : defaultMarkerIcon}
                      >
                        <Popup>
                          <div className="text-xs font-sans text-slate-900">
                            <strong>{node.camera_id}</strong>
                            <p>{node.name}</p>
                            <span className="text-[10px] text-slate-600">{node.sector}</span>
                          </div>
                        </Popup>
                      </Marker>
                    );
                  })}

                  {/* Highlight Active Path Polyline */}
                  {pathResult?.path_exists && (
                    <Polyline
                      positions={getActivePathCoordinates()}
                      color="#10b981"
                      weight={4}
                      opacity={0.85}
                      dashArray="8, 6"
                    />
                  )}
                </MapContainer>
              </div>

              {/* Path Node Sequence Pills */}
              {pathResult?.path_exists && (
                <div className="space-y-1.5 pt-1">
                  <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 block">
                    Traversed Camera Sequence:
                  </span>
                  <div className="flex flex-wrap items-center gap-1.5 text-xs font-mono">
                    {pathResult.camera_path.map((cid, idx) => (
                      <React.Fragment key={cid}>
                        <span className="px-2.5 py-1 rounded bg-slate-900 border border-slate-700 text-slate-200 font-bold">
                          {cid}
                        </span>
                        {idx < pathResult.camera_path.length - 1 && (
                          <ArrowRight className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                        )}
                      </React.Fragment>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Right Column: Kinematics & Feasibility Telemetry (5 cols) */}
            <div className="lg:col-span-5 flex flex-col gap-4">
              {/* Verdict Card */}
              <div className="bg-[#0D1525] border border-slate-800 rounded-xl p-5 shadow-lg space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                    <Activity className="w-4 h-4 text-emerald-400" />
                    <span>Transition Feasibility Verdict</span>
                  </h3>
                  <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${getStatusBadge(validationResult?.status || 'TEMPORALLY_FEASIBLE')}`}>
                    {validationResult?.status.replace(/_/g, ' ') || 'EVALUATING'}
                  </span>
                </div>

                {/* Kinematics Metric Tiles Grid */}
                <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                  <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                    <span className="text-[10px] text-slate-500 block uppercase font-bold">Path Distance</span>
                    <span className="text-base font-extrabold text-blue-400">
                      {Math.round(validationResult?.distance_meters || 0)} m
                    </span>
                    <span className="text-[10px] text-slate-500 block">
                      ({((validationResult?.distance_meters || 0) / 1000).toFixed(2)} km)
                    </span>
                  </div>

                  <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                    <span className="text-[10px] text-slate-500 block uppercase font-bold">Required Speed</span>
                    <span className={`text-base font-extrabold ${(validationResult?.speed_ratio || 0) > 1.2 ? 'text-rose-400' : 'text-emerald-400'}`}>
                      {validationResult?.required_average_speed_kmh || 0} km/h
                    </span>
                    <span className="text-[10px] text-slate-500 block">
                      Limit: {validationResult?.speed_limit_kmh || 50} km/h
                    </span>
                  </div>

                  <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                    <span className="text-[10px] text-slate-500 block uppercase font-bold">Feasible Time Window</span>
                    <span className="text-slate-200 font-bold">
                      {Math.round(validationResult?.minimum_time_seconds || 0)}s &ndash; {Math.round(validationResult?.maximum_reasonable_time_seconds || 0)}s
                    </span>
                  </div>

                  <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                    <span className="text-[10px] text-slate-500 block uppercase font-bold">Observed Transit</span>
                    <span className="text-amber-400 font-bold text-base">
                      {Math.round(validationResult?.observed_delta_seconds || 0)}s
                    </span>
                  </div>
                </div>

                {/* Explanation Box */}
                <div className="p-3.5 bg-slate-950 rounded-lg border border-slate-800 font-mono text-[11px] text-slate-300 leading-relaxed whitespace-pre-wrap">
                  {validationResult?.explanation || 'Calculating road graph kinematics...'}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: Demonstration Scenarios */}
      {activeTab === 'scenarios' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {demoScenarios.map((scen) => (
              <div
                key={scen.scenario_id}
                className="bg-[#0D1525] border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between gap-4"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${getStatusBadge(scen.validation_result.status)}`}>
                      {scen.validation_result.status.replace(/_/g, ' ')}
                    </span>
                    <span className="text-xs font-mono text-slate-400">
                      {scen.source_time} &rarr; {scen.target_time} ({scen.observed_delta_seconds}s)
                    </span>
                  </div>

                  <h3 className="text-sm font-bold text-white mb-1">{scen.title}</h3>
                  <p className="text-xs text-slate-400 mb-3">{scen.description}</p>

                  {/* Route & Distance */}
                  <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 font-mono text-xs space-y-1.5">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Route:</span>
                      <span className="text-blue-400 font-bold">{scen.source_camera_id} &rarr; {scen.target_camera_id}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Distance:</span>
                      <span className="text-slate-200">{scen.validation_result.distance_meters} m</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Required Speed:</span>
                      <span className="text-amber-400 font-bold">{scen.validation_result.required_average_speed_kmh} km/h</span>
                    </div>
                  </div>
                </div>

                {/* Explanation */}
                <div className="p-3 bg-slate-950/80 rounded-lg border border-slate-800 text-[11px] font-mono text-slate-300 leading-relaxed">
                  {scen.validation_result.explanation}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
