import pytest
import httpx
from app.main import app


@pytest.mark.anyio
async def test_simulation_run_status_and_cleanup_api():
    """Verify simulation run, status query, and cleanup endpoints via HTTP."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # 1. Clean previous simulation data
        cleanup_res = await client.post("/api/v1/simulation/cleanup")
        assert cleanup_res.status_code == 200

        # 2. Trigger simulation run via API
        run_res = await client.post("/api/v1/simulation/run", json={
            "vehicle_count": 15,
            "events_per_vehicle": 4,
            "seed": 42
        })
        assert run_res.status_code == 200
        run_data = run_res.json()
        assert run_data["status"] == "completed"
        assert run_data["vehicles_created"] == 15
        assert run_data["events_created"] > 30
        assert run_data["seed"] == 42

        # 3. Check simulation status
        status_res = await client.get("/api/v1/simulation/status")
        assert status_res.status_code == 200
        status_data = status_res.json()
        assert status_data["total_simulated_vehicles"] == 15
        assert status_data["total_simulated_events"] == run_data["events_created"]

        # 4. Query recent detections endpoint
        det_res = await client.get("/api/v1/detections/recent?limit=25")
        assert det_res.status_code == 200
        det_data = det_res.json()
        assert det_data["total"] == 25
        assert len(det_data["items"]) == 25

        first_det = det_data["items"][0]
        assert "detection_uid" in first_det
        assert "camera_code" in first_det
        assert "camera_name" in first_det
        assert "timestamp" in first_det
        assert first_det["is_simulated"] is True

        # 5. Query recent detections filtered by camera
        cam_det_res = await client.get("/api/v1/detections/recent?camera_id=CAM_PUN_001&limit=50")
        assert cam_det_res.status_code == 200
        cam_det_data = cam_det_res.json()
        for item in cam_det_data["items"]:
            assert item["camera_code"] == "CAM_PUN_001"

        # 6. Cleanup simulation records
        clean_res = await client.post("/api/v1/simulation/cleanup")
        assert clean_res.status_code == 200
        clean_data = clean_res.json()
        assert clean_data["vehicles_deleted"] == 15
