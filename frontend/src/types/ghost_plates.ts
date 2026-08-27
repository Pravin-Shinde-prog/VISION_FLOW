export interface PlateSighting {
  plate_number: string;
  camera_id: string;
  timestamp: string;
  detection_id?: number | null;
  vehicle_id?: number | null;
  ocr_confidence: number;
  vehicle_color?: string | null;
  vehicle_type?: string | null;
  aspect_ratio?: number | null;
  snapshot_path?: string | null;
}

export interface EvidenceItem {
  category: string;
  verdict: string; // CONSISTENT | CONTRADICTORY | INCONCLUSIVE | NORMAL
  description: string;
  severity_impact: number;
}

export interface GhostPlateAlertRecord {
  alert_id: string;
  plate_number: string;
  normalized_plate: string;
  alert_type: string; // POSSIBLE_CLONED_PLATE | TOPOLOGY_INCONSISTENT | NORMAL_REPEAT_SIGHTING | NO_ANOMALY
  severity: string; // CRITICAL | HIGH | MEDIUM | LOW | NONE
  status: string; // NEW | REVIEWED | DISMISSED | CONFIRMED_BY_OPERATOR
  source_camera_id: string;
  target_camera_id: string;
  source_timestamp: string;
  target_timestamp: string;
  observed_delta_seconds: number;
  minimum_feasible_time_seconds: number;
  distance_meters: number;
  required_speed_kmh: number;
  speed_limit_kmh: number;
  graph_status: string;
  anomaly_score: number;
  ocr_confidence_product: number;
  reid_similarity_score?: number | null;
  evidence_checklist: EvidenceItem[];
  explanation: string;
  source_snapshot_ref: string;
  target_snapshot_ref: string;
  is_simulated: boolean;
  created_at: string;
  analysis_latency_ms: number;
}

export interface GhostPlateAnalysisRequest {
  source_sighting: PlateSighting;
  target_sighting: PlateSighting;
  congestion_tolerance_factor?: number;
}

export interface LiveSightingEvaluationRequest {
  sighting: PlateSighting;
  history_window_minutes?: number;
}

export interface LiveSightingEvaluationResponse {
  evaluated_sighting: PlateSighting;
  previous_sightings_found: number;
  alerts_generated: GhostPlateAlertRecord[];
  is_suspicious: boolean;
  highest_anomaly_score: number;
  execution_latency_ms: number;
}

export interface GhostPlateStatusUpdate {
  status: string;
  notes?: string | null;
}

export interface GhostPlateScenario {
  scenario_id: string;
  title: string;
  description: string;
  expected_classification: string;
  expected_severity: string;
  alert: GhostPlateAlertRecord;
}
