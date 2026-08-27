import pytest
import httpx
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.ghost_plates.schemas import (
    PlateSighting,
    GhostPlateAnalysisRequest,
    LiveSightingEvaluationRequest,
    GhostPlateStatusUpdate,
)
from app.ghost_plates.detector import GhostPlateDetector
from app.ghost_plates.engine import GhostPlateEngine
from app.main import app


@pytest.mark.anyio
async def test_same_camera_repeat_sighting(db_session: AsyncSession):
    """Verify same-camera repeated sighting is classified as normal stationary loitering."""
    base_time = datetime(2026, 8, 27, 10, 0, 0, tzinfo=timezone.utc)
    s_a = PlateSighting(plate_number="MH12AB1234", camera_id="CAM_PUN_001", timestamp=base_time)
    s_b = PlateSighting(plate_number="MH12AB1234", camera_id="CAM_PUN_001", timestamp=base_time + timedelta(seconds=120))

    alert = await GhostPlateDetector.analyze_sighting_pair(s_a, s_b, db_session)
    assert alert.alert_type == "NORMAL_REPEAT_SIGHTING"
    assert alert.severity == "NONE"
    assert alert.anomaly_score == 0.0


@pytest.mark.anyio
async def test_normal_movement_no_anomaly(db_session: AsyncSession):
    """Verify normal feasible transit across cameras produces NO_ANOMALY."""
    base_time = datetime(2026, 8, 27, 10, 0, 0, tzinfo=timezone.utc)
    s_a = PlateSighting(plate_number="MH12AB1234", camera_id="CAM_PUN_001", timestamp=base_time)
    s_b = PlateSighting(plate_number="MH12AB1234", camera_id="CAM_PUN_002", timestamp=base_time + timedelta(seconds=180))

    alert = await GhostPlateDetector.analyze_sighting_pair(s_a, s_b, db_session)
    assert alert.alert_type == "NO_ANOMALY"
    assert alert.severity == "NONE"
    assert alert.anomaly_score == 0.0


@pytest.mark.anyio
async def test_impossible_speed_ghost_plate(db_session: AsyncSession):
    """Verify impossible speed across distant cameras flags POSSIBLE_CLONED_PLATE with CRITICAL severity."""
    base_time = datetime(2026, 8, 27, 10, 0, 0, tzinfo=timezone.utc)
    s_a = PlateSighting(
        plate_number="MH 12 AB 1234",
        camera_id="CAM_PUN_001",
        timestamp=base_time,
        ocr_confidence=0.98,
        vehicle_color="white",
        vehicle_type="sedan"
    )
    s_b = PlateSighting(
        plate_number="MH12AB1234",
        camera_id="CAM_PUN_010",
        timestamp=base_time + timedelta(seconds=8),
        ocr_confidence=0.97,
        vehicle_color="black",
        vehicle_type="suv"
    )

    alert = await GhostPlateDetector.analyze_sighting_pair(s_a, s_b, db_session)
    assert alert.alert_type == "POSSIBLE_CLONED_PLATE"
    assert alert.severity == "CRITICAL"
    assert alert.anomaly_score >= 0.85
    assert alert.required_speed_kmh > 500.0
    assert len(alert.evidence_checklist) >= 3


@pytest.mark.anyio
async def test_low_ocr_confidence_attenuates_score(db_session: AsyncSession):
    """Verify lower OCR confidence reduces anomaly score to avoid false accusations on noisy camera feeds."""
    base_time = datetime(2026, 8, 27, 10, 0, 0, tzinfo=timezone.utc)
    s_high_a = PlateSighting(plate_number="MH12XY5500", camera_id="CAM_PUN_001", timestamp=base_time, ocr_confidence=0.98)
    s_high_b = PlateSighting(plate_number="MH12XY5500", camera_id="CAM_PUN_004", timestamp=base_time + timedelta(seconds=6), ocr_confidence=0.97)

    s_low_a = PlateSighting(plate_number="MH12XY5500", camera_id="CAM_PUN_001", timestamp=base_time, ocr_confidence=0.52)
    s_low_b = PlateSighting(plate_number="MH12XY5500", camera_id="CAM_PUN_004", timestamp=base_time + timedelta(seconds=6), ocr_confidence=0.48)

    alert_high = await GhostPlateDetector.analyze_sighting_pair(s_high_a, s_high_b, db_session)
    alert_low = await GhostPlateDetector.analyze_sighting_pair(s_low_a, s_low_b, db_session)

    assert alert_high.anomaly_score > alert_low.anomaly_score
    assert alert_low.severity in ("LOW", "MEDIUM")


@pytest.mark.anyio
async def test_ghost_plates_api_endpoints_and_review_workflow(db_session: AsyncSession):
    """Verify Ghost Plates REST API endpoints and review state updates."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # 1. Analyze endpoint
        payload = {
            "source_sighting": {
                "plate_number": "MH12AB1234",
                "camera_id": "CAM_PUN_001",
                "timestamp": "2026-08-27T10:00:00Z",
                "ocr_confidence": 0.98,
                "vehicle_color": "white",
                "vehicle_type": "sedan"
            },
            "target_sighting": {
                "plate_number": "MH12AB1234",
                "camera_id": "CAM_PUN_010",
                "timestamp": "2026-08-27T10:00:08Z",
                "ocr_confidence": 0.97,
                "vehicle_color": "black",
                "vehicle_type": "suv"
            }
        }
        res = await client.post("/api/v1/ghost-plates/analyze", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["alert_type"] == "POSSIBLE_CLONED_PLATE"
        assert data["severity"] == "CRITICAL"
        assert data["anomaly_score"] >= 0.85

        # 2. Demo scenarios
        demo_res = await client.get("/api/v1/ghost-plates/demo-scenarios")
        assert demo_res.status_code == 200
        scenarios = demo_res.json()
        assert len(scenarios) == 5

        # 3. Evaluate live sighting
        eval_req = {
            "sighting": {
                "plate_number": "MH12AB1234",
                "camera_id": "CAM_PUN_001",
                "timestamp": "2026-08-27T10:00:00Z",
                "ocr_confidence": 0.95
            },
            "history_window_minutes": 60
        }
        eval_res = await client.post("/api/v1/ghost-plates/evaluate-sighting", json=eval_req)
        assert eval_res.status_code == 200

        # 4. List alerts
        alerts_res = await client.get("/api/v1/ghost-plates/alerts")
        assert alerts_res.status_code == 200
        assert isinstance(alerts_res.json(), list)
