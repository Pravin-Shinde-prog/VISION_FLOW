from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from app.reid.schemas import (
    VehicleVisualSignature,
    ReIDObservationPayload,
    ReIDDemoStep,
    ReIDDemoScenarioResponse,
)
from app.reid.engine import VehicleReIDEngine


class ReIDDemoScenarios:
    """
    Generates realistic multi-camera vehicle tracking demonstration scenarios:
    Vehicle travels across urban cameras while its license plate transitions from
    clean & readable -> occluded by road mud -> unreadable from severe headlight glare.
    Demonstrates how Multi-Feature Visual Re-ID preserves vehicle continuity.
    """

    @classmethod
    def get_multi_camera_muddy_plate_scenario(cls) -> ReIDDemoScenarioResponse:
        engine = VehicleReIDEngine()
        base_time = datetime(2026, 8, 27, 10, 30, 0, tzinfo=timezone.utc)

        # Tracked Target Vehicle: White Honda City Sedan (MH12AB1234)
        target_sig_initial = VehicleVisualSignature(
            vehicle_color="white",
            color_confidence=0.95,
            vehicle_type="sedan",
            type_confidence=0.92,
            make="Honda",
            model="City",
            aspect_ratio=1.65,
            distinctive_features=["roof_rails_none", "tint_light", "fastag_sticker"],
            plate_number="MH12AB1234",
            ocr_confidence=0.96,
        )

        # Step 1: Camera 1 - Deccan Gymkhana (Plate Normal / Readable)
        obs_1 = ReIDObservationPayload(
            observation_id="OBS_PUN_001",
            camera_id="CAM_PUN_001",
            timestamp=base_time,
            signature=target_sig_initial,
            lat=18.5167,
            lon=73.8415,
        )

        # Step 2: Camera 2 - FC Road Junction (Plate Mud-Covered / Occluded)
        target_sig_step2 = VehicleVisualSignature(
            vehicle_color="white",
            color_confidence=0.93,
            vehicle_type="sedan",
            type_confidence=0.90,
            make="Honda",
            model="City",
            aspect_ratio=1.62,
            distinctive_features=["roof_rails_none", "tint_light", "fastag_sticker"],
            plate_number=None,
            ocr_confidence=0.0,
        )
        obs_2 = ReIDObservationPayload(
            observation_id="OBS_PUN_002",
            camera_id="CAM_PUN_002",
            timestamp=base_time + timedelta(seconds=74),
            signature=target_sig_step2,
            lat=18.5204,
            lon=73.8432,
        )

        # Step 3: Camera 3 - Shivajinagar Interchange (Plate Glare / Unreadable)
        target_sig_step3 = VehicleVisualSignature(
            vehicle_color="white",
            color_confidence=0.88,
            vehicle_type="sedan",
            type_confidence=0.89,
            make="Honda",
            model="City",
            aspect_ratio=1.64,
            distinctive_features=["roof_rails_none", "tint_light", "fastag_sticker"],
            plate_number=None,
            ocr_confidence=0.0,
        )
        obs_3 = ReIDObservationPayload(
            observation_id="OBS_PUN_003",
            camera_id="CAM_PUN_003",
            timestamp=base_time + timedelta(seconds=168),
            signature=target_sig_step3,
            lat=18.5314,
            lon=73.8446,
        )

        # Live Re-ID Match Evaluations
        match_1_2 = engine.compare_observations(obs_1, obs_2)
        match_2_3 = engine.compare_observations(obs_2, obs_3)

        steps = [
            ReIDDemoStep(
                step_number=1,
                camera_id="CAM_PUN_001",
                camera_name="Deccan Gymkhana",
                timestamp="10:30:00",
                plate_display="MH12AB1234",
                plate_status="READABLE",
                ocr_confidence=0.96,
                vehicle_color="White",
                vehicle_type="Sedan",
                match_score=1.0,
                match_classification="HIGH_CONFIDENCE_MATCH",
                reid_method="PLATE_EXACT_MATCH",
                evidence_summary=[
                    "Origin sighting in Pune South corridor",
                    "High-security plate verified by ONNX ANPR (96% conf)",
                    "Visual baseline signature captured"
                ]
            ),
            ReIDDemoStep(
                step_number=2,
                camera_id="CAM_PUN_002",
                camera_name="FC Road Junction",
                timestamp="10:31:14 (+74s)",
                plate_display="UNREADABLE (Mud Occluded)",
                plate_status="OCCLUDED",
                ocr_confidence=None,
                vehicle_color="White",
                vehicle_type="Sedan",
                match_score=match_1_2.overall_score,
                match_classification=match_1_2.classification,
                reid_method=match_1_2.method_used,
                evidence_summary=[
                    "Plate unreadable due to heavy monsoon road spray",
                    f"Visual Re-ID Color Match: {int(match_1_2.evidence.color_similarity * 100)}%",
                    f"Visual Re-ID Type Match: {int(match_1_2.evidence.type_similarity * 100)}%",
                    f"Kinematics: 74s interval over {int(match_1_2.distance_meters or 450)}m corridor",
                    f"Continuous Track Retained: {int(match_1_2.overall_score * 100)}% confidence"
                ]
            ),
            ReIDDemoStep(
                step_number=3,
                camera_id="CAM_PUN_003",
                camera_name="Shivajinagar Interchange",
                timestamp="10:32:48 (+168s)",
                plate_display="UNREADABLE (Headlight Glare)",
                plate_status="UNREADABLE",
                ocr_confidence=None,
                vehicle_color="White",
                vehicle_type="Sedan",
                match_score=match_2_3.overall_score,
                match_classification=match_2_3.classification,
                reid_method=match_2_3.method_used,
                evidence_summary=[
                    "Plate overexposed by extreme headlight glare",
                    f"Visual Re-ID Appearance Match: {int(match_2_3.evidence.appearance_similarity * 100)}%",
                    f"Silhouette & Aspect Ratio Match: {int(match_2_3.evidence.shape_similarity * 100)}%",
                    f"Kinematics: 94s interval over {int(match_2_3.distance_meters or 1230)}m corridor",
                    f"Continuous Track Retained: {int(match_2_3.overall_score * 100)}% confidence"
                ]
            ),
        ]

        distractors = [
            {
                "vehicle_id": "DISTRACTOR_001",
                "color": "White",
                "type": "SUV",
                "plate": "MH12XY8844",
                "camera": "CAM_PUN_002",
                "similarity_with_target": 0.52,
                "rejection_reason": "Type mismatch (SUV vs Sedan) despite matching white color",
            },
            {
                "vehicle_id": "DISTRACTOR_002",
                "color": "Black",
                "type": "Sedan",
                "plate": "MH14EF3311",
                "camera": "CAM_PUN_002",
                "similarity_with_target": 0.38,
                "rejection_reason": "Color mismatch (Black vs White) despite matching Sedan body type",
            },
            {
                "vehicle_id": "DISTRACTOR_003",
                "color": "Silver",
                "type": "Hatchback",
                "plate": "MH12KM9001",
                "camera": "CAM_PUN_003",
                "similarity_with_target": 0.28,
                "rejection_reason": "Combined color, aspect ratio, and vehicle type divergence",
            },
        ]

        return ReIDDemoScenarioResponse(
            scenario_id="pune_corridor_muddy_plate_journey",
            title="Multi-Camera Occluded Plate Continuity (Deccan -> FC Road -> Shivajinagar)",
            description="Demonstrates uninterrupted vehicle tracking across 3 consecutive city cameras when license plates become occluded by mud and glare.",
            tracked_vehicle_id="VEH_PUN_9921",
            ground_truth_plate="MH12AB1234",
            steps=steps,
            distractor_vehicles=distractors,
            summary="Vehicle identity successfully preserved across all 3 cameras with >80% composite Re-ID confidence despite plate loss."
        )
