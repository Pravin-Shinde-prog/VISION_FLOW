from datetime import datetime, timezone
from fastapi import APIRouter, status, Response
from app.core.config import settings
from app.schemas.health import HealthResponse, DatabaseHealthResponse
from app.db.session import check_database_health

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse, summary="System Health Check")
async def get_health() -> HealthResponse:
    """
    Returns the operational health status and service metadata of the VISION_FLOW backend.
    """
    return HealthResponse(
        status="ok",
        service=f"{settings.PROJECT_NAME} backend",
        version=settings.VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
        environment=settings.ENVIRONMENT
    )


@router.get(
    "/health/database",
    response_model=DatabaseHealthResponse,
    summary="Database & PostGIS Health Check"
)
async def get_database_health(response: Response) -> DatabaseHealthResponse:
    """
    Performs a live query against PostgreSQL and verifies PostGIS extension status.
    Returns database name, PostGIS version, and query latency.
    """
    health_data = await check_database_health()
    if health_data["status"] != "ok":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return DatabaseHealthResponse(
        status=health_data["status"],
        database=health_data["database"],
        postgis_version=health_data["postgis_version"],
        latency_ms=health_data["latency_ms"],
        timestamp=datetime.now(timezone.utc).isoformat(),
        error=health_data["error"]
    )
