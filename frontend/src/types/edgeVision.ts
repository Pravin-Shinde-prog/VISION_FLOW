export interface ImageQualityMetrics {
  brightness_score: number;
  contrast_score: number;
  sharpness_score: number;
  glare_score: number;
  illumination_uniformity: number;
  overall_quality_score: number;
}

export interface PlateAnomalyFlags {
  missing_plate: boolean;
  broken_plate: boolean;
  damaged_plate: boolean;
  modified_plate: boolean;
  non_standard_plate: boolean;
  obscured_plate: boolean;
  unreadable_plate: boolean;
}

export interface CandidatePlateRegion {
  region_id: number;
  bbox: [number, number, number, number];
  confidence: number;
  aspect_ratio: number;
  plate_quality_score: number;
  plate_brightness: number;
  plate_contrast: number;
  plate_sharpness: number;
  plate_glare: number;
  condition: string; // NORMAL | PARTIAL | OCCLUDED | DAMAGED | UNREADABLE
  readability: string; // EXCELLENT | GOOD | FAIR | POOR | CRITICAL
  anomaly_flags: PlateAnomalyFlags;
  cropped_plate_b64?: string;
}

export interface EdgeVisionProcessResponse {
  data_source: string;
  pipeline_version: string;
  processed_at: string;
  camera_id?: string;
  frame_width: number;
  frame_height: number;
  processing_latency_ms: number;
  image_quality: ImageQualityMetrics;
  plate_detected: boolean;
  candidate_plates_count: number;
  candidate_plates: CandidatePlateRegion[];
  primary_plate?: CandidatePlateRegion | null;
  overall_anomaly_detected: boolean;
  summary_condition: string;
  enhanced_frame_b64?: string;
  edge_representation_b64?: string;
}

export interface SampleFrameInfo {
  sample_id: string;
  title: string;
  description: string;
  category: string;
  filename: string;
}

export interface PreprocessingOptions {
  camera_id?: string;
  enable_clahe?: boolean;
  clahe_clip_limit?: number;
  enable_denoising?: boolean;
  enable_sharpening?: boolean;
  sharpen_strength?: number;
  enable_glare_reduction?: boolean;
}
