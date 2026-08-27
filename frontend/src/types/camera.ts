export type CameraStatus = 'active' | 'online' | 'warning' | 'offline' | 'maintenance';

export interface CameraInstallationMetadata {
  is_simulated?: boolean;
  city?: string;
  resolution?: string;
  fps?: number;
  lanes_covered?: number;
  mount_height_m?: number;
  feed_protocol?: string;
  warning_note?: string;
  offline_reason?: string;
  [key: string]: unknown;
}

export interface Camera {
  id: number;
  camera_id: string;
  name: string;
  description?: string | null;
  latitude: number;
  longitude: number;
  direction_angle?: number | null;
  road_name?: string | null;
  sector?: string | null;
  status: CameraStatus;
  installation_metadata?: CameraInstallationMetadata | null;
  created_at: string;
  updated_at: string;
}

export interface CameraDetail extends Camera {
  outgoing_edges_count: number;
  incoming_edges_count: number;
  is_simulated: boolean;
}

export interface CameraListResponse {
  total: number;
  online_count: number;
  warning_count: number;
  offline_count: number;
  items: Camera[];
}

export interface RoadEdge {
  id: number;
  source_camera_id: number;
  destination_camera_id: number;
  source_camera_code: string;
  destination_camera_code: string;
  source_latitude: number;
  source_longitude: number;
  destination_latitude: number;
  destination_longitude: number;
  distance_meters: number;
  expected_min_travel_seconds: number;
  expected_max_travel_seconds?: number | null;
  speed_limit_kmh?: number | null;
  road_name?: string | null;
  direction?: string | null;
  is_active: boolean;
  created_at: string;
}

export interface RoadEdgeListResponse {
  total: number;
  items: RoadEdge[];
}
