import React, { useState } from 'react';
import {
  X,
  Video,
  Compass,
  MapPin,
  Activity,
  Layers,
  ArrowUpRight,
  ArrowDownLeft,
  Check,
  Copy,
  Info,
  Sliders,
  ShieldAlert,
  Radio
} from 'lucide-react';
import { Camera, RoadEdge } from '../../types/camera';

interface CameraDetailPanelProps {
  camera: Camera;
  roadEdges: RoadEdge[];
  onClose: () => void;
  onSelectConnectedCamera?: (cameraId: string) => void;
}

export const CameraDetailPanel: React.FC<CameraDetailPanelProps> = ({
  camera,
  roadEdges,
  onClose,
  onSelectConnectedCamera,
}) => {
  const [copied, setCopied] = useState(false);

  // Find incoming and outgoing edges for this camera
  const outgoingEdges = roadEdges.filter((e) => e.source_camera_code === camera.camera_id);
  const incomingEdges = roadEdges.filter((e) => e.destination_camera_code === camera.camera_id);

  const handleCopyCoords = () => {
    navigator.clipboard.writeText(`${camera.latitude.toFixed(6)}, ${camera.longitude.toFixed(6)}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getStatusBadge = () => {
    switch (camera.status.toLowerCase()) {
      case 'active':
      case 'online':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            ONLINE
          </span>
        );
      case 'warning':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30">
            <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
            WARNING
          </span>
        );
      case 'offline':
      case 'maintenance':
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/30">
            <span className="w-2 h-2 rounded-full bg-rose-500" />
            OFFLINE
          </span>
        );
    }
  };

  const metadata = camera.installation_metadata || {};

  return (
    <div className="bg-[#0D1525]/95 backdrop-blur-md border border-slate-700/70 rounded-xl p-5 shadow-2xl flex flex-col gap-4 text-slate-100 max-h-[80vh] overflow-y-auto">
      {/* Header */}
      <div className="flex items-start justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-blue-600/20 text-blue-400 rounded-lg border border-blue-500/30">
            <Video className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-sm font-bold text-blue-400 tracking-wider">
                {camera.camera_id}
              </span>
              {getStatusBadge()}
            </div>
            <h3 className="text-base font-bold text-slate-100 mt-0.5">{camera.name}</h3>
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-slate-200 hover:bg-slate-800 p-1.5 rounded-lg transition-colors"
          title="Close detail panel"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Prototype Simulated Data Notice */}
      <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-blue-950/40 border border-blue-800/40 text-blue-300 text-xs">
        <Info className="w-4 h-4 text-blue-400 shrink-0" />
        <span>Data source: Simulated Camera Network (Pune, Maharashtra)</span>
      </div>

      {/* Key Location Information */}
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="bg-slate-900/60 p-2.5 rounded-lg border border-slate-800">
          <span className="text-slate-400 flex items-center gap-1 mb-1">
            <MapPin className="w-3.5 h-3.5 text-slate-400" />
            Road / Corridor
          </span>
          <p className="font-semibold text-slate-200 truncate">{camera.road_name || 'N/A'}</p>
        </div>
        <div className="bg-slate-900/60 p-2.5 rounded-lg border border-slate-800">
          <span className="text-slate-400 flex items-center gap-1 mb-1">
            <Layers className="w-3.5 h-3.5 text-slate-400" />
            Urban Sector
          </span>
          <p className="font-semibold text-slate-200 truncate">{camera.sector || 'N/A'}</p>
        </div>
      </div>

      {/* GPS Coordinates & Orientation */}
      <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800 flex flex-col gap-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-400 flex items-center gap-1">
            <MapPin className="w-3.5 h-3.5 text-cyan-400" />
            GPS Position (WGS 84)
          </span>
          <button
            onClick={handleCopyCoords}
            className="flex items-center gap-1 text-[11px] text-cyan-400 hover:text-cyan-300 font-mono"
          >
            {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
            {copied ? 'Copied!' : 'Copy'}
          </button>
        </div>
        <div className="font-mono text-xs text-slate-300 flex justify-between bg-black/40 px-2.5 py-1.5 rounded border border-slate-800/80">
          <span>Lat: {camera.latitude.toFixed(6)}° N</span>
          <span>Lon: {camera.longitude.toFixed(6)}° E</span>
        </div>

        <div className="flex items-center justify-between text-xs pt-1 border-t border-slate-800/60">
          <span className="text-slate-400 flex items-center gap-1">
            <Compass className="w-3.5 h-3.5 text-amber-400" />
            Camera Direction Heading
          </span>
          <span className="font-mono font-semibold text-amber-300">
            {camera.direction_angle != null ? `${camera.direction_angle}°` : 'Omnidirectional'}
          </span>
        </div>
      </div>

      {/* Hardware & Stream Telemetry */}
      <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800 text-xs flex flex-col gap-2">
        <span className="text-slate-400 flex items-center gap-1 font-semibold uppercase tracking-wider text-[10px]">
          <Sliders className="w-3.5 h-3.5 text-blue-400" />
          Hardware & Edge Telemetry
        </span>
        <div className="grid grid-cols-2 gap-2">
          <div>
            <span className="text-slate-500 block text-[11px]">Resolution</span>
            <span className="font-mono font-semibold text-slate-200">
              {String(metadata.resolution || '1080p')}
            </span>
          </div>
          <div>
            <span className="text-slate-500 block text-[11px]">Edge FPS</span>
            <span className="font-mono font-semibold text-slate-200">
              {metadata.fps != null ? `${metadata.fps} FPS` : '30 FPS'}
            </span>
          </div>
          <div>
            <span className="text-slate-500 block text-[11px]">Mount Height</span>
            <span className="font-mono font-semibold text-slate-200">
              {metadata.mount_height_m != null ? `${metadata.mount_height_m}m` : '7.0m'}
            </span>
          </div>
          <div>
            <span className="text-slate-500 block text-[11px]">Protocol</span>
            <span className="font-mono font-semibold text-slate-200">
              {String(metadata.feed_protocol || 'RTSP/H.265')}
            </span>
          </div>
        </div>

        {metadata.warning_note && (
          <div className="mt-1 flex items-start gap-1.5 p-2 rounded bg-amber-950/30 border border-amber-700/40 text-amber-300 text-[11px]">
            <ShieldAlert className="w-3.5 h-3.5 shrink-0 mt-0.5" />
            <span>{String(metadata.warning_note)}</span>
          </div>
        )}
        {metadata.offline_reason && (
          <div className="mt-1 flex items-start gap-1.5 p-2 rounded bg-rose-950/30 border border-rose-700/40 text-rose-300 text-[11px]">
            <Radio className="w-3.5 h-3.5 shrink-0 mt-0.5" />
            <span>{String(metadata.offline_reason)}</span>
          </div>
        )}
      </div>

      {/* Network Topology: Connected Road Edges */}
      <div className="flex flex-col gap-2 text-xs">
        <span className="text-slate-400 flex items-center gap-1 font-semibold uppercase tracking-wider text-[10px]">
          <Activity className="w-3.5 h-3.5 text-emerald-400" />
          Connected Road Network ({outgoingEdges.length + incomingEdges.length} Links)
        </span>

        {/* Outgoing Connections */}
        <div className="flex flex-col gap-1">
          <span className="text-slate-400 text-[11px] flex items-center gap-1">
            <ArrowUpRight className="w-3 h-3 text-cyan-400" />
            Outgoing Connections ({outgoingEdges.length})
          </span>
          {outgoingEdges.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {outgoingEdges.map((edge) => (
                <button
                  key={edge.id}
                  onClick={() => onSelectConnectedCamera?.(edge.destination_camera_code)}
                  className="px-2 py-1 bg-slate-900 hover:bg-cyan-950/60 border border-slate-700 hover:border-cyan-500/50 rounded text-cyan-300 font-mono text-[11px] transition-all flex items-center gap-1"
                  title={`${edge.road_name || 'Road'}: ${edge.distance_meters}m (min ${edge.expected_min_travel_seconds}s)`}
                >
                  <span>→ {edge.destination_camera_code}</span>
                  <span className="text-slate-500 text-[10px]">({Math.round(edge.distance_meters)}m)</span>
                </button>
              ))}
            </div>
          ) : (
            <span className="text-slate-500 italic text-[11px]">No registered outgoing routes</span>
          )}
        </div>

        {/* Incoming Connections */}
        <div className="flex flex-col gap-1 mt-1">
          <span className="text-slate-400 text-[11px] flex items-center gap-1">
            <ArrowDownLeft className="w-3 h-3 text-amber-400" />
            Incoming Connections ({incomingEdges.length})
          </span>
          {incomingEdges.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {incomingEdges.map((edge) => (
                <button
                  key={edge.id}
                  onClick={() => onSelectConnectedCamera?.(edge.source_camera_code)}
                  className="px-2 py-1 bg-slate-900 hover:bg-amber-950/60 border border-slate-700 hover:border-amber-500/50 rounded text-amber-300 font-mono text-[11px] transition-all flex items-center gap-1"
                  title={`${edge.road_name || 'Road'}: ${edge.distance_meters}m (min ${edge.expected_min_travel_seconds}s)`}
                >
                  <span>← {edge.source_camera_code}</span>
                  <span className="text-slate-500 text-[10px]">({Math.round(edge.distance_meters)}m)</span>
                </button>
              ))}
            </div>
          ) : (
            <span className="text-slate-500 italic text-[11px]">No registered incoming routes</span>
          )}
        </div>
      </div>
    </div>
  );
};
