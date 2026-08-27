export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  timestamp: string;
  environment: string;
}

export type HealthStatus = 'online' | 'offline' | 'loading';

export interface SystemStatusState {
  status: HealthStatus;
  data: HealthResponse | null;
  error: string | null;
  lastChecked: Date | null;
  latencyMs: number | null;
}
