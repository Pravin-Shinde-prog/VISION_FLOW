export interface SimulationRunRequest {
  vehicle_count: number;
  events_per_vehicle: number;
  seed?: number;
  start_time?: string;
}

export interface SimulationRunResponse {
  status: string;
  vehicles_created: number;
  plates_created: number;
  events_created: number;
  seed?: number;
  start_time: string;
  end_time: string;
  duration_seconds: number;
  message: string;
}

export interface SimulationStatusResponse {
  is_running: boolean;
  total_simulated_vehicles: number;
  total_simulated_events: number;
  total_simulated_plates: number;
  last_run_seed?: number;
  last_simulation_time?: string;
}

export interface SimulationCleanupResponse {
  status: string;
  detections_deleted: number;
  plates_deleted: number;
  vehicles_deleted: number;
  message: string;
}
