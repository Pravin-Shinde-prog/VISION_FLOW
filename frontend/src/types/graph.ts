export interface GraphNode {
  camera_id: string;
  name: string;
  latitude: number;
  longitude: number;
  sector: string;
  road_name?: string | null;
  is_active: boolean;
}

export interface GraphEdge {
  edge_id: number;
  source_camera_id: string;
  destination_camera_id: string;
  distance_meters: number;
  speed_limit_kmh: number;
  expected_min_travel_seconds: number;
  expected_max_travel_seconds: number;
  road_name?: string | null;
  direction?: string | null;
}

export interface GraphTopologyResponse {
  total_nodes: number;
  total_edges: number;
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface GraphPathResponse {
  path_exists: boolean;
  source_camera_id: string;
  target_camera_id: string;
  camera_path: string[];
  node_names_path: string[];
  edge_ids: number[];
  total_distance_meters: number;
  estimated_min_time_seconds: number;
  estimated_max_time_seconds: number;
  effective_speed_limit_kmh: number;
  hop_count: number;
  explanation: string;
}

export interface TransitionValidationRequest {
  source_camera_id: string;
  target_camera_id: string;
  source_timestamp: string;
  target_timestamp: string;
  vehicle_id?: string | null;
  plate_number?: string | null;
  reid_confidence?: number | null;
  congestion_tolerance_factor?: number;
}

export interface TransitionValidationResponse {
  status: string; // TEMPORALLY_FEASIBLE | TOO_FAST | TOO_SLOW | NO_FEASIBLE_PATH | SAME_LOCATION_STATIONARY
  source_camera_id: string;
  target_camera_id: string;
  observed_delta_seconds: number;
  path_exists: boolean;
  camera_path: string[];
  distance_meters: number;
  minimum_time_seconds: number;
  maximum_reasonable_time_seconds: number;
  required_average_speed_kmh: number;
  speed_limit_kmh: number;
  speed_ratio: number;
  transition_feasibility_score: number;
  reid_confidence?: number | null;
  explanation: string;
  validation_latency_ms: number;
}

export interface SequenceObservation {
  observation_id: string;
  camera_id: string;
  timestamp: string;
  plate_number?: string | null;
  vehicle_color?: string | null;
  vehicle_type?: string | null;
  reid_confidence?: number | null;
}

export interface SequenceValidationRequest {
  observations: SequenceObservation[];
  congestion_tolerance_factor?: number;
}

export interface SequenceValidationResponse {
  total_hops: number;
  feasible_hops: number;
  anomalous_hops: number;
  overall_route_feasible: boolean;
  transitions: TransitionValidationResponse[];
  summary_explanation: string;
  execution_latency_ms: number;
}

export interface GraphDemoScenario {
  scenario_id: string;
  title: string;
  description: string;
  source_camera_id: string;
  target_camera_id: string;
  source_time: string;
  target_time: string;
  observed_delta_seconds: number;
  expected_status: string;
  category: string;
  validation_result: TransitionValidationResponse;
}
