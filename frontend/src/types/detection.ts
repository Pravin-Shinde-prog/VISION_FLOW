export interface Detection {
  id: number;
  detection_uid: string;
  camera_id: number;
  camera_code: string;
  camera_name: string;
  vehicle_id?: number | null;
  vehicle_uid?: string | null;
  plate_id?: number | null;
  plate_number?: string | null;
  timestamp: string;
  ocr_confidence?: number | null;
  vehicle_color?: string | null;
  vehicle_type?: string | null;
  direction_travel?: string | null;
  snapshot_path?: string | null;
  plate_anomaly_flags?: Record<string, unknown> | null;
  processing_metadata?: Record<string, unknown> | null;
  association_confidence?: number | null;
  is_simulated: boolean;
  created_at: string;
}

export interface DetectionListResponse {
  total: number;
  items: Detection[];
}
