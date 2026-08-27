from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., description="System operational status, e.g. 'ok'")
    service: str = Field(..., description="Service identifier name")
    version: str = Field(..., description="API version")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp of the health check"
    )
    environment: str = Field(default="development", description="Current deployment environment")


class DatabaseHealthResponse(BaseModel):
    status: str = Field(..., description="Database operational status, 'ok' or 'error'")
    database: str = Field(..., description="Connected PostgreSQL database name")
    postgis_version: Optional[str] = Field(None, description="Active PostGIS extension version string")
    latency_ms: Optional[float] = Field(None, description="Roundtrip query latency in milliseconds")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp of the database check"
    )
    error: Optional[str] = Field(None, description="Detailed error description if connection failed")
