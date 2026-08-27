import { ImageQualityMetrics, PlateAnomalyFlags } from './edgeVision';

export interface PlateComponents {
  state_code?: string | null;
  district_code?: string | null;
  series?: string | null;
  registration_number?: string | null;
}

export interface PlateOCRResult {
  raw_text: string;
  normalized_plate?: string | null;
  ocr_confidence: number;
  format_valid: boolean;
  final_confidence: number;
  readability: string; // READABLE | LOW_CONFIDENCE | UNREADABLE
  components?: PlateComponents | null;
  ocr_engine: string;
  engine_version: string;
  ocr_latency_ms: number;
}

export interface ANPRCandidateResult {
  region_id: number;
  bbox: [number, number, number, number];
  confidence: number;
  aspect_ratio: number;
  plate_quality_score: number;
  condition: string;
  anomaly_flags: PlateAnomalyFlags;
  ocr_result: PlateOCRResult;
  rank_score: number;
  cropped_plate_b64?: string;
}

export interface ANPRProcessResponse {
  data_source: string;
  pipeline_version: string;
  processed_at: string;
  camera_id?: string | null;
  frame_width: number;
  frame_height: number;
  total_latency_ms: number;
  edge_vision_latency_ms: number;
  ocr_latency_ms: number;
  plate_detected: boolean;
  primary_plate?: ANPRCandidateResult | null;
  all_candidates: ANPRCandidateResult[];
  image_quality: ImageQualityMetrics;
  summary_condition: string;
  annotated_frame_b64?: string;
  cropped_plate_b64?: string;
  persisted_detection_id?: number | null;
}

export interface ANPRBenchmarkResultItem {
  sample_id: string;
  title: string;
  category: string;
  expected_plate?: string | null;
  raw_extracted?: string | null;
  normalized_extracted?: string | null;
  format_valid: boolean;
  exact_match: boolean;
  normalized_match: boolean;
  latency_ms: number;
  readability: string;
  final_confidence: number;
}

export interface ANPRBenchmarkResponse {
  total_samples: number;
  exact_matches: number;
  exact_match_rate: number;
  normalized_matches: number;
  normalized_match_rate: number;
  format_valid_count: number;
  format_valid_rate: number;
  average_latency_ms: number;
  results_breakdown: ANPRBenchmarkResultItem[];
  disclaimer: string;
}
