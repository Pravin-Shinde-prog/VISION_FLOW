from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory for the backend package (VISION_FLOW/backend)
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    PROJECT_NAME: str = "VISION_FLOW"
    PROJECT_TITLE: str = "City-Wide AI Engine for Multi-Camera ANPR Trajectory Tracking and Urban Traffic Analytics"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # CORS configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    # Database Configuration (PostgreSQL + PostGIS)
    DATABASE_URL: Optional[str] = None
    POSTGRES_USER: str = "visionflow"
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_SERVER: str = "127.0.0.1"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "vision_flow"

    # Connection Pool Settings
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_ECHO: bool = False

    @property
    def async_database_url(self) -> str:
        """
        Constructs or returns the asyncpg database connection URL.
        """
        if self.DATABASE_URL:
            # Ensure proper asyncpg driver prefix
            if self.DATABASE_URL.startswith("postgresql://"):
                return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
            return self.DATABASE_URL

        password_part = f":{self.POSTGRES_PASSWORD}" if self.POSTGRES_PASSWORD else ""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}{password_part}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(
        env_file=(str(BACKEND_DIR / ".env"), ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
