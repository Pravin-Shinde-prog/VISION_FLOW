import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from app.core.config import settings
from app.db.session import get_db
from app.main import app


@pytest.fixture(autouse=True)
def override_db_dependency():
    """
    Overrides the FastAPI get_db dependency to use a fresh NullPool engine per test.
    This guarantees that every test event loop owns its own database connections
    without sharing pooled connections across different asyncio loops.
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

    async def _test_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with test_session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = _test_get_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Direct session fixture with NullPool for unit tests that query the DB directly.
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
