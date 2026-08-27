import React, { useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Polyline, Tooltip, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Camera, RoadEdge } from '../../types/camera';

interface CameraMapProps {
  cameras: Camera[];
  roadEdges: RoadEdge[];
  selectedCamera: Camera | null;
  onSelectCamera: (camera: Camera) => void;
  showEdges?: boolean;
  mapTheme?: 'dark' | 'standard';
}

// Controller component to smoothly auto-fit camera network bounds
const MapBoundsController: React.FC<{ cameras: Camera[]; selectedCamera: Camera | null }> = ({
  cameras,
  selectedCamera,
}) => {
  const map = useMap();

  useEffect(() => {
    if (selectedCamera) {
      map.flyTo([selectedCamera.latitude, selectedCamera.longitude], 15, {
        duration: 0.8,
      });
      return;
    }

    if (cameras.length > 0) {
      const bounds = L.latLngBounds(cameras.map((c) => [c.latitude, c.longitude]));
      map.fitBounds(bounds, { padding: [50, 50], maxZoom: 14 });
    }
  }, [cameras, selectedCamera, map]);

  return null;
};

// Generates an interactive, styled SVG divIcon for a camera node
function createCameraIcon(camera: Camera, isSelected: boolean): L.DivIcon {
  const status = camera.status.toLowerCase();
  let bgClass = 'bg-emerald-500 text-emerald-950 border-emerald-300';
  let pulseClass = 'marker-pulse-active ring-emerald-500/50';

  if (status === 'warning') {
    bgClass = 'bg-amber-500 text-amber-950 border-amber-300';
    pulseClass = 'marker-pulse-warning ring-amber-500/50';
  } else if (status === 'offline' || status === 'maintenance') {
    bgClass = 'bg-rose-500 text-rose-950 border-rose-300';
    pulseClass = 'ring-rose-500/30';
  }

  const selectedRing = isSelected
    ? 'scale-125 ring-4 ring-cyan-400 z-50 drop-shadow-[0_0_12px_rgba(6,182,212,0.9)]'
    : 'hover:scale-110';

  const headingAngle = camera.direction_angle != null ? camera.direction_angle : 0;

  const html = `
    <div class="relative flex items-center justify-center cursor-pointer transition-transform duration-200 ${selectedRing}">
      <!-- Heading Arrow Indicator -->
      <div 
        class="absolute -top-1.5 w-3 h-3 flex items-center justify-center transition-transform" 
        style="transform: rotate(${headingAngle}deg) translateY(-10px);"
      >
        <svg class="w-3.5 h-3.5 text-cyan-300 drop-shadow" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2L4 14h6v8h4v-8h6z" />
        </svg>
      </div>

      <!-- Core Camera Circle -->
      <div class="w-8 h-8 rounded-full ${bgClass} ${pulseClass} border-2 flex items-center justify-center shadow-lg font-bold text-[11px] select-none">
        <svg class="w-4 h-4 text-slate-950" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="m22 8-6 4 6 4V8Z"/>
          <rect width="14" height="12" x="2" y="6" rx="2"/>
        </svg>
      </div>

      <!-- Compact Camera Code Label -->
      <div class="absolute -bottom-4 bg-slate-950/90 text-slate-200 border border-slate-700/80 px-1.5 py-0.5 rounded text-[9px] font-mono font-bold whitespace-nowrap shadow">
        ${camera.camera_id}
      </div>
    </div>
  `;

  return L.divIcon({
    html,
    className: 'custom-camera-div-icon',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    tooltipAnchor: [0, -18],
  });
}

// Direction arrow icon for the midpoint of directed road edges
function createDirectionArrowIcon(angleDeg: number, color: string): L.DivIcon {
  const html = `
    <div style="transform: rotate(${angleDeg}deg); color: ${color};" class="flex items-center justify-center drop-shadow">
      <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 4l-8 16h6v4h4v-4h6z" />
      </svg>
    </div>
  `;
  return L.divIcon({
    html,
    className: 'custom-edge-arrow-icon',
    iconSize: [16, 16],
    iconAnchor: [8, 8],
  });
}

export const CameraMap: React.FC<CameraMapProps> = ({
  cameras,
  roadEdges,
  selectedCamera,
  onSelectCamera,
  showEdges = true,
  mapTheme = 'dark',
}) => {
  // Default map center on Pune city center
  const defaultCenter: [number, number] = [18.5308, 73.8475];

  // Pre-calculate edge midpoint positions and orientation angles for direction markers
  const edgeArrows = useMemo(() => {
    return roadEdges.map((edge) => {
      const midLat = (edge.source_latitude + edge.destination_latitude) / 2;
      const midLon = (edge.source_longitude + edge.destination_longitude) / 2;

      // Calculate bearing angle from source to destination
      const dLon = ((edge.destination_longitude - edge.source_longitude) * Math.PI) / 180;
      const lat1 = (edge.source_latitude * Math.PI) / 180;
      const lat2 = (edge.destination_latitude * Math.PI) / 180;
      const y = Math.sin(dLon) * Math.cos(lat2);
      const x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLon);
      const bearingRad = Math.atan2(y, x);
      const bearingDeg = (bearingRad * 180) / Math.PI;

      const isConnectedToSelected =
        selectedCamera &&
        (edge.source_camera_code === selectedCamera.camera_id ||
          edge.destination_camera_code === selectedCamera.camera_id);

      const color = isConnectedToSelected
        ? edge.source_camera_code === selectedCamera?.camera_id
          ? '#22d3ee' // Cyan for Outgoing from selected
          : '#fbbf24' // Amber for Incoming to selected
        : '#38bdf8'; // Blue for normal

      return {
        id: edge.id,
        position: [midLat, midLon] as [number, number],
        icon: createDirectionArrowIcon(bearingDeg, color),
        edge,
      };
    });
  }, [roadEdges, selectedCamera]);

  return (
    <div className={`w-full h-full relative rounded-xl overflow-hidden ${mapTheme === 'dark' ? 'dark-tiles' : ''}`}>
      <MapContainer
        center={defaultCenter}
        zoom={13}
        scrollWheelZoom={true}
        className="w-full h-full z-0 bg-[#0B0F17]"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          maxZoom={19}
        />

        <MapBoundsController cameras={cameras} selectedCamera={selectedCamera} />

        {/* Directed Road Connections (Polylines) */}
        {showEdges &&
          roadEdges.map((edge) => {
            const isOutgoing = selectedCamera?.camera_id === edge.source_camera_code;
            const isIncoming = selectedCamera?.camera_id === edge.destination_camera_code;
            const isHighlighted = isOutgoing || isIncoming;

            let strokeColor = '#0284c7';
            let strokeWidth = 2.5;
            let strokeDash = '4, 6';

            if (isOutgoing) {
              strokeColor = '#06b6d4'; // Cyan
              strokeWidth = 4;
              strokeDash = '';
            } else if (isIncoming) {
              strokeColor = '#f59e0b'; // Amber
              strokeWidth = 4;
              strokeDash = '';
            }

            return (
              <React.Fragment key={`edge-${edge.id}`}>
                <Polyline
                  positions={[
                    [edge.source_latitude, edge.source_longitude],
                    [edge.destination_latitude, edge.destination_longitude],
                  ]}
                  pathOptions={{
                    color: strokeColor,
                    weight: strokeWidth,
                    opacity: isHighlighted ? 0.95 : 0.6,
                    dashArray: strokeDash,
                  }}
                >
                  <Tooltip sticky direction="top" className="custom-edge-tooltip">
                    <div className="font-mono text-xs p-1">
                      <div className="font-bold text-cyan-300">
                        {edge.source_camera_code} → {edge.destination_camera_code}
                      </div>
                      <div className="text-slate-300">{edge.road_name || 'Corridor Link'}</div>
                      <div className="text-slate-400 text-[10px] mt-0.5">
                        Dist: {Math.round(edge.distance_meters)}m | Est: {Math.round(edge.expected_min_travel_seconds)}s | Max: {edge.speed_limit_kmh} km/h
                      </div>
                    </div>
                  </Tooltip>
                </Polyline>
              </React.Fragment>
            );
          })}

        {/* Direction Flow Markers on Edges */}
        {showEdges &&
          edgeArrows.map((arrow) => (
            <Marker
              key={`arrow-${arrow.id}`}
              position={arrow.position}
              icon={arrow.icon}
              interactive={false}
            />
          ))}

        {/* Camera Markers */}
        {cameras.map((camera) => {
          const isSelected = selectedCamera?.camera_id === camera.camera_id;
          const icon = createCameraIcon(camera, isSelected);

          return (
            <Marker
              key={camera.camera_id}
              position={[camera.latitude, camera.longitude]}
              icon={icon}
              eventHandlers={{
                click: () => onSelectCamera(camera),
              }}
            >
              <Tooltip direction="top" offset={[0, -16]}>
                <div className="text-xs">
                  <div className="font-bold text-blue-400 font-mono">{camera.camera_id}</div>
                  <div className="font-medium text-slate-100">{camera.name}</div>
                  <div className="text-slate-400 text-[10px]">
                    Status: <span className="capitalize text-slate-200">{camera.status}</span>
                  </div>
                </div>
              </Tooltip>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
};
