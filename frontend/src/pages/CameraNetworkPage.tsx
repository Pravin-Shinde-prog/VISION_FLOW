import React from 'react';
import { Video } from 'lucide-react';
import { PlaceholderView } from '../components/common/PlaceholderView';

export const CameraNetworkPage: React.FC = () => {
  return (
    <PlaceholderView
      title="GIS Camera Network & Spatial Topology"
      stageNumber="Stage 6"
      stageName="Stage 6 (GIS & Camera Network)"
      icon={Video}
      description="Interactive GIS mapping canvas displaying all simulated and edge-connected camera installations, coverage angles, active health status, and live feed previews."
      plannedFeatures={[
        {
          title: "Interactive Leaflet / GIS Map Canvas",
          desc: "City-wide map with interactive camera markers, status indicators, and road link polylines.",
        },
        {
          title: "Multi-Feed Live Monitoring Grid",
          desc: "Simultaneous playback grid for simulated/prerecorded traffic feeds and active edge streams.",
        },
        {
          title: "Camera Node Metadata & Health Monitor",
          desc: "Status, orientation, frame rate, and operational uptime tracking for every municipal node.",
        },
        {
          title: "Spatial Selection & Route Inspection",
          desc: "Interactive lasso and corridor selection to query camera clusters and road segments.",
        },
      ]}
    />
  );
};
