import { HealthResponse } from '../types/health';

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
      headers: {
        'Accept': 'application/json',
      },
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
