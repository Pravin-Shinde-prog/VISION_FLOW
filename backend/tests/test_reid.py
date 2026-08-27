import pytest
import httpx
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.reid.color_extractor import VehicleColorExtractor
from app.reid.feature_extractor import VisualFeatureExtractor
from app.reid.spatial_temporal import SpatialTemporalValidator
from app.reid.similarity import ReIDSimilarityCalculator
from app.reid.engine import VehicleReIDEngine
from app.reid.demo_scenarios import ReIDDemoScenarios
from app.reid.schemas import (
    VehicleVisualSignature,
    ReIDObservationPayload,
    ReIDMatchRequest,
)
from app.main import app


def test_color_similarity_and_extraction():
    """Verify deterministic color similarity and perceptual relationships."""
    # 1. Exact matches
    assert VehicleColorExtractor.compute_similarity("white", "white") == 1.0
    assert VehicleColorExtractor.compute_similarity("Black", "black") == 1.0

    # 2. Perceptually close
    assert VehicleColorExtractor.compute_similarity("white", "silver") == 0.70
    assert VehicleColorExtractor.compute_similarity("silver", "grey") == 0.80

    # 3. Mismatch
    assert VehicleColorExtractor.compute_similarity("white", "black") == 0.05
    assert VehicleColorExtractor.compute_similarity("red", "blue") == 0.05

    # 4. Unknown handling
    assert VehicleColorExtractor.compute_similarity("unknown", "white") == 0.50


def test_reid_similarity_and_occluded_plate_fallback():
    """Verify visual Re-ID fallback when license plates are unreadable."""
    # Sighting A (Plate readable)
    sig_a = VehicleVisualSignature(
        vehicle_color="white",
        vehicle_type="sedan",
        aspect_ratio=1.6,
        plate_number="MH12AB1234",
        ocr_confidence=0.95,
    )

    # Sighting B (Plate unreadable / muddy)
    sig_b = VehicleVisualSignature(
        vehicle_color="white",
        vehicle_type="sedan",
        aspect_ratio=1.6,
        plate_number=None,
        ocr_confidence=0.0,
    )

    res = ReIDSimilarityCalculator.calculate_similarity(sig_a, sig_b)
    assert res.method_used == "VISUAL_REID_FALLBACK"
    assert res.is_match is True
    assert res.overall_score >= 0.75
    assert res.evidence.color_similarity == 1.0
    assert res.evidence.type_similarity == 1.0
    assert res.evidence.plate_similarity is None
    assert "Visual Re-ID" in res.explanation


def test_multi_feature_discrimination_between_vehicles():
    """Verify multi-feature discrimination prevents false positives."""
    # Target: White Sedan
    sig_target = VehicleVisualSignature(vehicle_color="white", vehicle_type="sedan", aspect_ratio=1.6)

    # Distractor 1: White SUV (Same color, different body type)
    sig_suv = VehicleVisualSignature(vehicle_color="white", vehicle_type="suv", aspect_ratio=1.2)
    res_suv = ReIDSimilarityCalculator.calculate_similarity(sig_target, sig_suv)

    # Distractor 2: Black Sedan (Same type, different color)
    sig_black_sedan = VehicleVisualSignature(vehicle_color="black", vehicle_type="sedan", aspect_ratio=1.6)
    res_black_sedan = ReIDSimilarityCalculator.calculate_similarity(sig_target, sig_black_sedan)

    # Both distractors should have significantly lower scores than matching white sedan
    sig_white_sedan = VehicleVisualSignature(vehicle_color="white", vehicle_type="sedan", aspect_ratio=1.6)
    res_match = ReIDSimilarityCalculator.calculate_similarity(sig_target, sig_white_sedan)

    assert res_match.overall_score > res_suv.overall_score
    assert res_match.overall_score > res_black_sedan.overall_score
    assert res_suv.evidence.type_similarity < 0.20
    assert res_black_sedan.evidence.color_similarity < 0.10


def test_spatial_temporal_kinematics():
    """Verify distance, velocity, and plausibility gates."""
    t1 = datetime(2026, 8, 27, 10, 0, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 8, 27, 10, 2, 0, tzinfo=timezone.utc)  # 120s later

    # Distance between Pune Deccan (18.5167, 73.8415) and FC Road (18.5204, 73.8432) ~450m
    dt, dist, speed, is_plausible = SpatialTemporalValidator.evaluate(
        time_a=t1, time_b=t2,
        lat_a=18.5167, lon_a=73.8415,
        lat_b=18.5204, lon_b=73.8432
    )
    assert dt == 120.0
    assert 400.0 <= dist <= 600.0
    assert speed < 30.0  # Urban corridor speed ~13.5 km/h
    assert is_plausible is True

    # Impossible speed test (Distance 50km in 10s)
    _, _, speed_fast, is_plausible_fast = SpatialTemporalValidator.evaluate(
        time_a=t1, time_b=t1 + timedelta(seconds=10),
        lat_a=18.5167, lon_a=73.8415,
        lat_b=19.0760, lon_b=72.8777  # Mumbai (~120km away)
    )
    assert is_plausible_fast is False


@pytest.mark.anyio
async def test_reid_api_endpoints(db_session: AsyncSession):
    """Verify Re-ID REST API endpoints."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # 1. Match two observations
        req_payload = {
            "source": {
                "observation_id": "OBS_001",
                "camera_id": "CAM_PUN_001",
                "signature": {
                    "vehicle_color": "white",
                    "vehicle_type": "sedan",
                    "aspect_ratio": 1.6,
                    "plate_number": "MH12AB1234",
                    "ocr_confidence": 0.95
                }
            },
            "target": {
                "observation_id": "OBS_002",
                "camera_id": "CAM_PUN_002",
                "signature": {
                    "vehicle_color": "white",
                    "vehicle_type": "sedan",
                    "aspect_ratio": 1.6,
                    "plate_number": None,
                    "ocr_confidence": 0.0
                }
            }
        }
        match_res = await client.post("/api/v1/reid/match", json=req_payload)
        assert match_res.status_code == 200
        data = match_res.json()
        assert data["is_match"] is True
        assert data["overall_score"] >= 0.70
        assert data["method_used"] == "VISUAL_REID_FALLBACK"

        # 2. Get Demo Scenario
        demo_res = await client.get("/api/v1/reid/demo-scenario")
        assert demo_res.status_code == 200
        demo_data = demo_res.json()
        assert len(demo_data["steps"]) == 3
        assert len(demo_data["distractor_vehicles"]) >= 2
        assert demo_data["ground_truth_plate"] == "MH12AB1234"
