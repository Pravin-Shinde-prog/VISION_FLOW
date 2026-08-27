import pytest
import httpx
from app.main import app


@pytest.mark.anyio
async def test_list_cameras_api():
    """Verify GET /api/v1/cameras returns all seeded cameras and summary counts."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/cameras")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 15
        assert data["online_count"] >= 12
        assert data["warning_count"] == 2
        assert data["offline_count"] == 1
        assert len(data["items"]) == 15

        # Check first camera fields
        cam = data["items"][0]
        assert "camera_id" in cam
        assert "latitude" in cam
        assert "longitude" in cam
        assert "status" in cam
        assert "road_name" in cam
        assert "sector" in cam


@pytest.mark.anyio
async def test_get_camera_by_id_success():
    """Verify GET /api/v1/cameras/{camera_id} returns detailed metadata."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/cameras/CAM_PUN_001")
        assert response.status_code == 200
        data = response.json()
        assert data["camera_id"] == "CAM_PUN_001"
        assert data["name"] == "Shivaji Nagar Junction"
        assert data["status"] == "active"
        assert data["latitude"] == pytest.approx(18.5308, 0.001)
        assert data["longitude"] == pytest.approx(73.8475, 0.001)
        assert data["outgoing_edges_count"] >= 3  # Branches to FC Road, Sancheti, SB Road
        assert data["is_simulated"] is True


@pytest.mark.anyio
async def test_get_camera_by_id_not_found():
    """Verify GET /api/v1/cameras/{camera_id} returns 404 for invalid ID."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/cameras/CAM_NONEXISTENT_999")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


@pytest.mark.anyio
async def test_list_road_edges_api():
    """Verify GET /api/v1/cameras/edges returns directed topological road segments."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/cameras/edges")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 17
        assert len(data["items"]) == 17

        # Check edge structure
        edge = data["items"][0]
        assert "source_camera_code" in edge
        assert "destination_camera_code" in edge
        assert "source_latitude" in edge
        assert "destination_latitude" in edge
        assert "distance_meters" in edge
        assert "expected_min_travel_seconds" in edge
        assert edge["is_active"] is True


@pytest.mark.anyio
async def test_nearby_cameras_spatial_query():
    """Verify GET /api/v1/cameras/nearby uses PostGIS to calculate proximity."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Search within 3km of Shivaji Nagar (18.5308, 73.8475)
        response = await client.get("/api/v1/cameras/nearby?latitude=18.5308&longitude=73.8475&radius_km=3.0")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

        # Closest camera should be CAM_PUN_001 itself with dist ~0m
        closest = data[0]
        assert closest["camera_id"] == "CAM_PUN_001"
        assert closest["distance_from_query_meters"] < 20.0  # Within 20 meters


@pytest.mark.anyio
async def test_camera_status_and_sector_filters():
    """Verify query filtering by status and sector."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Filter by status=offline
        res_offline = await client.get("/api/v1/cameras?status=offline")
        assert res_offline.status_code == 200
        data_offline = res_offline.json()
        assert data_offline["total"] == 1
        assert data_offline["items"][0]["camera_id"] == "CAM_PUN_013"

        # Filter by sector=Deccan
        res_deccan = await client.get("/api/v1/cameras?sector=Deccan")
        assert res_deccan.status_code == 200
        data_deccan = res_deccan.json()
        assert data_deccan["total"] == 3
