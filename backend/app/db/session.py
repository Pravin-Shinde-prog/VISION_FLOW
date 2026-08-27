import time
from typing import AsyncGenerator, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine
)
from app.core.config import settings

# Create Async SQLAlchemy Engine with connection health checking
engine: AsyncEngine = create_async_engine(
    settings.async_database_url,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_pre_ping=True,
    echo=settings.DB_ECHO,
    future=True
)

# Async Session Factory
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an asynchronous database session.
    Ensures sessions are closed and rolled back on unhandled exceptions.
    """
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_database_health() -> Dict[str, Any]:
    """
    Executes a live query to verify PostgreSQL connectivity and PostGIS availability.
    Returns operational metadata including database name, PostGIS version, and latency.
    """
    start_time = time.perf_counter()
    try:
        async with async_session_factory() as session:
            # Query current database name and PostGIS version
            result = await session.execute(
                text("SELECT current_database(), PostGIS_Version();")
            )
            row = result.fetchone()

            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

            if row:
                db_name, postgis_ver = row[0], row[1]
                return {
                    "status": "ok",
                    "database": db_name,
                    "postgis_version": postgis_ver,
                    "latency_ms": latency_ms,
                    "error": None
                }
            else:
                return {
                    "status": "error",
                    "database": settings.POSTGRES_DB,
                    "postgis_version": None,
                    "latency_ms": latency_ms,
                    "error": "Query returned no rows"
                }
    except Exception as exc:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return {
            "status": "error",
            "database": settings.POSTGRES_DB,
            "postgis_version": None,
            "latency_ms": latency_ms,
            "error": str(exc)
        }
