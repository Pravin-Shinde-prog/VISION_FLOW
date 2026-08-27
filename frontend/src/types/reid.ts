export interface VehicleVisualSignature {
  vehicle_color: string;
  color_confidence: number;
  vehicle_type: string;
  type_confidence: number;
  make?: string | null;
  model?: string | null;
  aspect_ratio: number;
  appearance_descriptor?: number[] | null;
  distinctive_features: string[];
  plate_number?: string | null;
  ocr_confidence?: number | null;
}

export interface FeatureSimilarityBreakdown {
  color_similarity: number;
  type_similarity: number;
  appearance_similarity: number;
  shape_similarity: number;
  plate_similarity?: number | null;
  distinctive_features_similarity: number;
  weights_applied: Record<string, number>;
}

export interface ReIDMatchResult {
  is_match: boolean;
  classification: string; // HIGH_CONFIDENCE_MATCH | POSSIBLE_MATCH | LOW_CONFIDENCE | NO_MATCH
  overall_score: number;
  evidence: FeatureSimilarityBreakdown;
  delta_time_seconds?: number | null;
  distance_meters?: number | null;
  speed_kmh?: number | null;
  is_temporally_plausible: boolean;
  method_used: string; // PLATE_AND_VISUAL_REID | VISUAL_REID_FALLBACK | PLATE_EXACT_MATCH
  explanation: string;
  reid_latency_ms: number;
}

export interface ReIDObservationPayload {
  observation_id?: string | null;
  camera_id?: string | null;
  timestamp?: string | null;
  signature: VehicleVisualSignature;
  lat?: number | null;
  lon?: number | null;
}

export interface ReIDMatchRequest {
  source: ReIDObservationPayload;
  target: ReIDObservationPayload;
  persist_match?: boolean;
}

export interface ReIDTrackCandidate {
  candidate_id: string;
  detection_id?: number | null;
  camera_id: string;
  camera_name?: string | null;
  timestamp: string;
  plate_number?: string | null;
  plate_readable: boolean;
  vehicle_color: string;
  vehicle_type: string;
  match_result: ReIDMatchResult;
}

export interface ReIDTrackResponse {
  source_observation_id: string;
  source_camera_id: string;
  source_plate?: string | null;
  source_color: string;
  source_type: string;
  total_candidates_evaluated: number;
  ranked_candidates: ReIDTrackCandidate[];
  execution_latency_ms: number;
}

export interface ReIDDemoStep {
  step_number: number;
  camera_id: string;
  camera_name: string;
  timestamp: string;
  plate_display: string;
  plate_status: string;
  ocr_confidence?: number | null;
  vehicle_color: string;
  vehicle_type: string;
  match_score: number;
  match_classification: string;
  reid_method: string;
  evidence_summary: string[];
}

export interface ReIDDemoScenarioResponse {
  scenario_id: string;
  title: string;
  description: string;
  tracked_vehicle_id: string;
  ground_truth_plate: string;
  steps: ReIDDemoStep[];
  distractor_vehicles: Array<{
    vehicle_id: string;
    color: string;
    type: string;
    plate: string;
    camera: string;
    similarity_with_target: number;
    rejection_reason: string;
  }>;
  summary: string;
}
