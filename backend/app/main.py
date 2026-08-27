from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_v1_router
from app.schemas.health import HealthResponse, DatabaseHealthResponse
from app.db.session import engine, check_database_health


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: verification
    yield
    # Shutdown: dispose of database connection pool cleanly
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_TITLE,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


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
async def api_database_health(response: Response) -> DatabaseHealthResponse:
    """
    Top-level health check endpoint for PostgreSQL & PostGIS status.
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


@app.get("/", tags=["Root"], summary="Root Status")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/api/health",
        "database_health": "/api/health/database"
    }
