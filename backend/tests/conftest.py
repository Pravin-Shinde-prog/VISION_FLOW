import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from app.core.config import settings

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Creates an isolated async database session with NullPool for testing.
    Prevents cross-event-loop connection reuse issues during pytest runs.
    """
    test_engine = create_async_engine(
        settings.async_database_url,
        poolclass=NullPool,
        echo=False
    )
    test_session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )

    async with test_session_factory() as session:
        yield session

    await test_engine.dispose()
