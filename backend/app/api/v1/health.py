from datetime import datetime, timezone
from fastapi import APIRouter
from app.core.config import settings
from app.schemas.health import HealthResponse

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
