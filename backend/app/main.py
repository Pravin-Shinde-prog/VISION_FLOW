from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Response, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import engine, check_database_health, get_db
from app.api.v1.router import api_v1_router
from app.schemas.health import HealthResponse, DatabaseHealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Verifies database connectivity on startup and cleanly closes the connection pool on shutdown.
    """
    print(f"[*] Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]")
    db_health = await check_database_health()
    if db_health["status"] == "ok":
        print(f"[+] Connected to PostgreSQL: {db_health['database']} (PostGIS {db_health['postgis_version']}) in {db_health['latency_ms']}ms")
    else:
        print(f"[!] Database check warning: {db_health['error']}")
    yield
    print(f"[*] Disposing database engine connection pool for {settings.PROJECT_NAME}...")
    await engine.dispose()
    print("[+] Database connection pool disposed cleanly.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="City-Wide AI Engine for Multi-Camera ANPR Trajectory Tracking and Urban Traffic Analytics",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Top-level direct health endpoint: GET /api/health
@app.get(
    "/api/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Top-level Service Health Endpoint"
)
async def api_health() -> HealthResponse:
    """
    Top-level health check endpoint for frontend / reverse-proxy status monitors.
    """
    return HealthResponse(
        status="ok",
        service=f"{settings.PROJECT_NAME} backend",
        version=settings.VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
        environment=settings.ENVIRONMENT
    )


# Top-level direct database health endpoint: GET /api/health/database
@app.get(
    "/api/health/database",
    response_model=DatabaseHealthResponse,
    tags=["Health"],
    summary="Top-level Database & PostGIS Health Endpoint"
)
async def api_database_health(
    response: Response,
    db: AsyncSession = Depends(get_db)
) -> DatabaseHealthResponse:
    """
    Top-level health check endpoint for PostgreSQL & PostGIS status.
    """
    health_data = await check_database_health(session=db)
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


# Mount API V1 Modular Router
app.include_router(api_v1_router, prefix=settings.API_V1_STR)
