export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  timestamp: string;
  environment: string;
}

export interface DatabaseHealthResponse {
  status: string;
  database: string;
  postgis_version: string | null;
  latency_ms: number | null;
  timestamp: string;
  error: string | null;
}

export type HealthStatus = 'online' | 'offline' | 'loading';

export interface SystemStatusState {
  status: HealthStatus;
  data: HealthResponse | null;
  error: string | null;
  lastChecked: Date | null;
  latencyMs: number | null;
}

export interface DatabaseStatusState {
  status: HealthStatus;
  data: DatabaseHealthResponse | null;
  error: string | null;
  latencyMs: number | null;
}
