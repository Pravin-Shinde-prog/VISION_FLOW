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
