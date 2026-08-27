import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Activity,
  Video,
  Search,
  RefreshCw,
  Car,
  ShieldCheck,
  AlertTriangle,
  AlertCircle,
  Filter
} from 'lucide-react';
import { Detection } from '../../types/detection';
import { fetchRecentDetections } from '../../services/api';

interface RecentDetectionsTableProps {
  refreshTrigger?: number;
}

export const RecentDetectionsTable: React.FC<RecentDetectionsTableProps> = ({
  refreshTrigger = 0,
}) => {
  const [detections, setDetections] = useState<Detection[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [searchPlate, setSearchPlate] = useState<string>('');
  const [selectedCamera, setSelectedCamera] = useState<string>('all');
  const [autoRefresh, setAutoRefresh] = useState<boolean>(true);

  const loadDetections = useCallback(async () => {
    try {
      setError(null);
      const res = await fetchRecentDetections({ limit: 50 });
      setDetections(res.items);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to fetch detections';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDetections();
  }, [loadDetections, refreshTrigger]);

  // Auto-refresh interval (every 8 seconds when enabled)
  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(() => {
      loadDetections();
    }, 8000);
    return () => clearInterval(interval);
  }, [autoRefresh, loadDetections]);

  // Extract unique cameras for filter dropdown
  const uniqueCameras = useMemo(() => {
    const map = new Map<string, string>();
    detections.forEach((d) => {
      if (d.camera_code) map.set(d.camera_code, d.camera_name);
    });
    return Array.from(map.entries()).map(([code, name]) => ({ code, name }));
  }, [detections]);

  // Filtered detections
  const filteredDetections = useMemo(() => {
    return detections.filter((det) => {
      const matchesPlate =
        searchPlate.trim() === '' ||
        (det.plate_number && det.plate_number.toLowerCase().includes(searchPlate.toLowerCase())) ||
        (det.vehicle_uid && det.vehicle_uid.toLowerCase().includes(searchPlate.toLowerCase()));

      const matchesCamera =
        selectedCamera === 'all' || det.camera_code === selectedCamera;

      return matchesPlate && matchesCamera;
    });
  }, [detections, searchPlate, selectedCamera]);

  const getConfidenceBadge = (confidence?: number | null) => {
    if (confidence == null) {
      return (
        <span className="text-[11px] font-mono text-slate-500 italic">
          N/A (Occluded)
        </span>
      );
    }
    const pct = Math.round(confidence * 100);
    if (pct >= 85) {
      return (
        <span className="inline-flex items-center gap-1 font-mono text-xs font-semibold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
          <ShieldCheck className="w-3 h-3" />
          {pct}%
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 font-mono text-xs font-semibold px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30">
        <AlertTriangle className="w-3 h-3" />
        {pct}%
      </span>
    );
  };

  return (
    <div className="bg-[#0D1525] border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col gap-4 text-slate-100">
      {/* Table Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-emerald-600/20 text-emerald-400 rounded-lg border border-emerald-500/30">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-white">Live Camera Telemetry & Sighting Feed</h2>
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                DATABASE BACKED
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Real-time camera observations with simulated ANPR OCR confidence and vehicle classification metadata.
            </p>
          </div>
        </div>

        {/* Toolbar */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Auto Refresh Toggle */}
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border text-xs font-semibold transition-all ${
              autoRefresh
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                : 'bg-slate-900 text-slate-400 border-slate-800'
            }`}
          >
            <span className={`w-2 h-2 rounded-full ${autoRefresh ? 'bg-emerald-500 animate-pulse' : 'bg-slate-500'}`} />
            <span>Auto-Feed (8s)</span>
          </button>

          {/* Refresh Button */}
          <button
            onClick={loadDetections}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 rounded-lg text-xs font-semibold disabled:opacity-50 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-rose-950/40 border border-rose-800/60 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Filter Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2.5">
        {/* Search Plate */}
        <div className="relative flex-1 max-w-sm">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search plate number (e.g. MH12)..."
            value={searchPlate}
            onChange={(e) => setSearchPlate(e.target.value)}
            className="w-full pl-9 pr-3.5 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        {/* Camera Filter Dropdown */}
        <div className="flex items-center gap-1.5 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800 text-xs">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={selectedCamera}
            onChange={(e) => setSelectedCamera(e.target.value)}
            className="bg-transparent text-slate-200 focus:outline-none cursor-pointer pr-2"
          >
            <option value="all" className="bg-slate-900 text-slate-200">
              All Camera Nodes ({uniqueCameras.length})
            </option>
            {uniqueCameras.map((cam) => (
              <option key={cam.code} value={cam.code} className="bg-slate-900 text-slate-200">
                {cam.code} - {cam.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Table Content */}
      <div className="overflow-x-auto rounded-lg border border-slate-800 max-h-[480px]">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-900/80 text-[11px] uppercase tracking-wider text-slate-400 font-mono sticky top-0 backdrop-blur z-10 border-b border-slate-800">
            <tr>
              <th className="py-3 px-3.5">Timestamp</th>
              <th className="py-3 px-3.5">Camera Node</th>
              <th className="py-3 px-3.5">Observed Plate</th>
              <th className="py-3 px-3.5">OCR Confidence</th>
              <th className="py-3 px-3.5">Vehicle Details</th>
              <th className="py-3 px-3.5">Direction</th>
              <th className="py-3 px-3.5">Compliance / Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-sans">
            {filteredDetections.map((det) => {
              const formattedTime = new Date(det.timestamp).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
              });
              const formattedDate = new Date(det.timestamp).toLocaleDateString([], {
                month: 'short',
                day: 'numeric',
              });

              return (
                <tr key={det.id} className="hover:bg-slate-900/50 transition-colors">
                  {/* Timestamp */}
                  <td className="py-2.5 px-3.5 whitespace-nowrap font-mono text-[11px]">
                    <div className="text-slate-200 font-semibold">{formattedTime}</div>
                    <div className="text-slate-500 text-[10px]">{formattedDate}</div>
                  </td>

                  {/* Camera */}
                  <td className="py-2.5 px-3.5 whitespace-nowrap">
                    <div className="flex items-center gap-1.5">
                      <Video className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                      <span className="font-mono font-bold text-blue-400">{det.camera_code}</span>
                    </div>
                    <div className="text-[10px] text-slate-400 truncate max-w-[140px]">
                      {det.camera_name}
                    </div>
                  </td>

                  {/* License Plate */}
                  <td className="py-2.5 px-3.5 whitespace-nowrap">
                    {det.plate_number ? (
                      <div className="inline-flex items-center gap-1.5 px-2 py-1 rounded bg-slate-900 border border-slate-700 font-mono font-bold text-xs text-amber-300 shadow-sm">
                        <span className="text-[9px] px-1 py-0.2 rounded bg-blue-600/80 text-white font-bold">
                          IND
                        </span>
                        <span>{det.plate_number}</span>
                      </div>
                    ) : (
                      <span className="inline-flex items-center px-2 py-0.5 rounded bg-rose-950/40 border border-rose-800/60 text-rose-300 font-mono text-[10px]">
                        OCCLUDED / NO OCR
                      </span>
                    )}
                  </td>

                  {/* Confidence */}
                  <td className="py-2.5 px-3.5 whitespace-nowrap">
                    {getConfidenceBadge(det.ocr_confidence)}
                  </td>

                  {/* Vehicle Details */}
                  <td className="py-2.5 px-3.5 whitespace-nowrap">
                    <div className="flex items-center gap-1.5">
                      <Car className="w-3.5 h-3.5 text-slate-400" />
                      <span className="font-semibold text-slate-200">
                        {det.vehicle_color || 'Unknown'} {det.vehicle_type || 'Vehicle'}
                      </span>
                    </div>
                    {det.vehicle_uid && (
                      <span className="text-[10px] text-slate-500 font-mono block">
                        UID: {det.vehicle_uid.slice(0, 16)}...
                      </span>
                    )}
                  </td>

                  {/* Direction */}
                  <td className="py-2.5 px-3.5 whitespace-nowrap font-mono text-[11px] text-slate-300">
                    {det.direction_travel || 'Inbound'}
                  </td>

                  {/* Compliance / Status */}
                  <td className="py-2.5 px-3.5 whitespace-nowrap">
                    {det.plate_anomaly_flags?.is_broken ? (
                      <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30 text-[10px] font-mono font-semibold">
                        Broken Plate
                      </span>
                    ) : det.plate_anomaly_flags?.is_missing ? (
                      <span className="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30 text-[10px] font-mono font-semibold">
                        Plate Missing
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-mono font-semibold">
                        Compliant
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}

            {filteredDetections.length === 0 && !isLoading && (
              <tr>
                <td colSpan={7} className="py-12 text-center text-slate-500 text-xs">
                  No detection sightings match your query. Run the traffic simulation to generate observations.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Footer info */}
      <div className="flex flex-col sm:flex-row items-center justify-between text-[11px] text-slate-500 font-mono">
        <span>Showing {filteredDetections.length} most recent sightings</span>
        <span>Snapshot protocol: simulated://camera/CAM_ID/event/EVT_ID.jpg</span>
      </div>
    </div>
  );
};
