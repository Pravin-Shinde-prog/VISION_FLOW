import pytest
import httpx
from app.main import app


@pytest.mark.anyio
async def test_top_level_health():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "VISION_FLOW" in data["service"]
        assert "timestamp" in data


@pytest.mark.anyio
async def test_v1_health():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


@pytest.mark.anyio
async def test_database_health_and_postgis():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Test top-level /api/health/database
        response = await client.get("/api/health/database")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["database"] == "vision_flow"
        assert data["postgis_version"] is not None
        assert "3.6" in data["postgis_version"]
        assert isinstance(data["latency_ms"], (int, float))

        # Test v1 /api/v1/health/database
        v1_response = await client.get("/api/v1/health/database")
        assert v1_response.status_code == 200
        v1_data = v1_response.json()
        assert v1_data["status"] == "ok"
        assert v1_data["database"] == "vision_flow"
        assert "3.6" in v1_data["postgis_version"]
