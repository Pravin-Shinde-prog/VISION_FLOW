import { HealthResponse, DatabaseHealthResponse } from '../types/health';
import { CameraListResponse, CameraDetail, RoadEdgeListResponse, Camera } from '../types/camera';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

export interface HealthCheckResult {
  data: HealthResponse;
  latencyMs: number;
}

/**
 * Calls backend GET /api/health to retrieve operational status and calculate latency.
 */
export async function checkBackendHealth(): Promise<HealthCheckResult> {
  const startTime = performance.now();
  const url = `${API_BASE}/api/health`;

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });

    const endTime = performance.now();
    const latencyMs = Math.round(endTime - startTime);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data: HealthResponse = await response.json();
    return { data, latencyMs };
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Unknown network error';
    throw new Error(`Backend unreachable (${message})`);
  }
}

/**
 * Calls backend GET /api/health/database to verify PostgreSQL and PostGIS health.
 */
export async function checkDatabaseHealth(): Promise<DatabaseHealthResponse> {
  const url = `${API_BASE}/api/health/database`;

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });

    const data: DatabaseHealthResponse = await response.json();
    if (!response.ok || data.status !== 'ok') {
      throw new Error(data.error || `HTTP ${response.status}: ${response.statusText}`);
    }

    return data;
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Database check failed';
    throw new Error(message);
  }
}

/**
 * Fetches all registered cameras with optional status or sector filtering.
 */
export async function fetchCameras(params?: { status?: string; sector?: string }): Promise<CameraListResponse> {
  const query = new URLSearchParams();
  if (params?.status && params.status !== 'all') query.append('status', params.status);
  if (params?.sector && params.sector !== 'all') query.append('sector', params.sector);

  const url = `${API_BASE}/api/v1/cameras${query.toString() ? `?${query.toString()}` : ''}`;
  const response = await fetch(url, {
    method: 'GET',
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch cameras: HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Fetches detailed metadata for a specific camera node.
 */
export async function fetchCameraById(cameraId: string): Promise<CameraDetail> {
  const url = `${API_BASE}/api/v1/cameras/${encodeURIComponent(cameraId)}`;
  const response = await fetch(url, {
    method: 'GET',
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch camera ${cameraId}: HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Fetches all directed road network connections for GIS rendering.
 */
export async function fetchRoadEdges(isActiveOnly = true): Promise<RoadEdgeListResponse> {
  const url = `${API_BASE}/api/v1/cameras/edges?is_active_only=${isActiveOnly}`;
  const response = await fetch(url, {
    method: 'GET',
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch road edges: HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Executes a PostGIS spatial query for cameras within a radius from a point.
 */
export async function fetchNearbyCameras(lat: number, lon: number, radiusKm = 5.0): Promise<Camera[]> {
  const url = `${API_BASE}/api/v1/cameras/nearby?latitude=${lat}&longitude=${lon}&radius_km=${radiusKm}`;
  const response = await fetch(url, {
    method: 'GET',
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    throw new Error(`Spatial query failed: HTTP ${response.status}`);
  }

  return response.json();
}

import {
  SimulationRunRequest,
  SimulationRunResponse,
  SimulationStatusResponse,
  SimulationCleanupResponse,
} from '../types/simulation';
import { DetectionListResponse } from '../types/detection';

/**
 * Triggers a synthetic traffic simulation run.
 */
export async function runSimulation(req: SimulationRunRequest): Promise<SimulationRunResponse> {
  const url = `${API_BASE}/api/v1/simulation/run`;
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(req),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Simulation run failed: HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Fetches current counts of simulated entities.
 */
export async function getSimulationStatus(): Promise<SimulationStatusResponse> {
  const url = `${API_BASE}/api/v1/simulation/status`;
  const response = await fetch(url, {
    method: 'GET',
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch simulation status: HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Purges all synthetic simulation records from the database.
 */
export async function cleanupSimulation(): Promise<SimulationCleanupResponse> {
  const url = `${API_BASE}/api/v1/simulation/cleanup`;
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    throw new Error(`Cleanup failed: HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Retrieves recent detection sightings from all cameras.
 */
export async function fetchRecentDetections(params?: {
  limit?: number;
  camera_id?: string;
  plate_number?: string;
}): Promise<DetectionListResponse> {
  const query = new URLSearchParams();
  if (params?.limit) query.append('limit', params.limit.toString());
  if (params?.camera_id) query.append('camera_id', params.camera_id);
  if (params?.plate_number) query.append('plate_number', params.plate_number);

  const url = `${API_BASE}/api/v1/detections/recent${query.toString() ? `?${query.toString()}` : ''}`;
  const response = await fetch(url, {
    method: 'GET',
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch recent detections: HTTP ${response.status}`);
  }

  return response.json();
}

import {
  SampleFrameInfo,
  EdgeVisionProcessResponse,
  PreprocessingOptions,
} from '../types/edgeVision';

/**
 * Fetches built-in sample test frame catalog for interactive testing.
 */
export async function fetchSampleFrames(): Promise<SampleFrameInfo[]> {
  const url = `${API_BASE}/api/v1/edge-vision/samples`;
  const response = await fetch(url, {
    method: 'GET',
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch sample frames: HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Runs the edge vision pipeline on a built-in test scenario on demand.
 */
export async function processSampleFrame(
  sampleId: string,
  options?: PreprocessingOptions
): Promise<EdgeVisionProcessResponse> {
  const query = new URLSearchParams();
  if (options?.camera_id) query.append('camera_id', options.camera_id);
  if (options?.enable_clahe !== undefined) query.append('enable_clahe', options.enable_clahe.toString());
  if (options?.clahe_clip_limit !== undefined) query.append('clahe_clip_limit', options.clahe_clip_limit.toString());
  if (options?.enable_denoising !== undefined) query.append('enable_denoising', options.enable_denoising.toString());
  if (options?.enable_sharpening !== undefined) query.append('enable_sharpening', options.enable_sharpening.toString());
  if (options?.sharpen_strength !== undefined) query.append('sharpen_strength', options.sharpen_strength.toString());
  if (options?.enable_glare_reduction !== undefined) query.append('enable_glare_reduction', options.enable_glare_reduction.toString());

  const url = `${API_BASE}/api/v1/edge-vision/samples/${encodeURIComponent(sampleId)}/process${
    query.toString() ? `?${query.toString()}` : ''
  }`;

  const response = await fetch(url, {
    method: 'GET',
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || `Edge Vision processing failed: HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Uploads a local image file and processes it through the Edge Vision pipeline.
 */
export async function processUploadedFrame(
  file: File,
  options?: PreprocessingOptions
): Promise<EdgeVisionProcessResponse> {
  const formData = new FormData();
  formData.append('file', file);
  if (options?.camera_id) formData.append('camera_id', options.camera_id);
  if (options?.enable_clahe !== undefined) formData.append('enable_clahe', options.enable_clahe.toString());
  if (options?.clahe_clip_limit !== undefined) formData.append('clahe_clip_limit', options.clahe_clip_limit.toString());
  if (options?.enable_denoising !== undefined) formData.append('enable_denoising', options.enable_denoising.toString());
  if (options?.enable_sharpening !== undefined) formData.append('enable_sharpening', options.enable_sharpening.toString());
  if (options?.sharpen_strength !== undefined) formData.append('sharpen_strength', options.sharpen_strength.toString());
  if (options?.enable_glare_reduction !== undefined) formData.append('enable_glare_reduction', options.enable_glare_reduction.toString());

  const url = `${API_BASE}/api/v1/edge-vision/process`;
  const response = await fetch(url, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || `Upload processing failed: HTTP ${response.status}`);
  }

  return response.json();
}

import {
  ANPRProcessResponse,
  ANPRBenchmarkResponse,
} from '../types/anpr';

/**
 * Runs end-to-end ANPR OCR pipeline on a sample scenario.
 */
export async function processANPRSample(
  sampleId: string,
  persist: boolean = false
): Promise<ANPRProcessResponse> {
  const url = `${API_BASE}/api/v1/anpr/samples/${encodeURIComponent(sampleId)}/process?persist=${persist}`;
  const response = await fetch(url, {
    method: 'GET',
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || `ANPR processing failed: HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Uploads a local image file and processes it through the ANPR OCR pipeline.
 */
export async function processANPRUpload(
  file: File,
  persist: boolean = false
): Promise<ANPRProcessResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('persist', persist.toString());

  const url = `${API_BASE}/api/v1/anpr/process`;
  const response = await fetch(url, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || `ANPR upload processing failed: HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Executes automated benchmark evaluation across test scenarios.
 */
export async function runANPRBenchmark(): Promise<ANPRBenchmarkResponse> {
  const url = `${API_BASE}/api/v1/anpr/benchmark`;
  const response = await fetch(url, {
    method: 'GET',
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    throw new Error(`Failed to run ANPR benchmark: HTTP ${response.status}`);
  }

  return response.json();
}

import {
  ReIDMatchRequest,
  ReIDMatchResult,
  ReIDObservationPayload,
  ReIDTrackResponse,
  ReIDDemoScenarioResponse,
} from '../types/reid';

/**
 * Matches two vehicle sightings using multi-feature Re-ID.
 */
export async function matchVehicleObservations(
  req: ReIDMatchRequest
): Promise<ReIDMatchResult> {
  const url = `${API_BASE}/api/v1/reid/match`;
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(req),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || `Re-ID match failed: HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Searches the camera network for sightings matching a target vehicle.
 */
export async function trackVehicle(
  source: ReIDObservationPayload
): Promise<ReIDTrackResponse> {
  const url = `${API_BASE}/api/v1/reid/track`;
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(source),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || `Vehicle tracking failed: HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Fetches the pre-built multi-camera occluded plate tracking demonstration scenario.
 */
export async function fetchReIDDemoScenario(): Promise<ReIDDemoScenarioResponse> {
  const url = `${API_BASE}/api/v1/reid/demo-scenario`;
  const response = await fetch(url, {
    method: 'GET',
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch Re-ID demo scenario: HTTP ${response.status}`);
  }

  return response.json();
}
