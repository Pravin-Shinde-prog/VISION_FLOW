from datetime import datetime, timezone
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
