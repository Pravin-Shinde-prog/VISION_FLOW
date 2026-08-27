from datetime import datetime, timezone, timedelta
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.ghost_plates.schemas import PlateSighting, GhostPlateScenario
from app.ghost_plates.detector import GhostPlateDetector


class GhostPlateDemoScenarios:
    """
    Provides 5 reproducible test scenarios illustrating Ghost / Cloned Plate anomaly detection:
    1. Normal Feasible Movement
    2. Impossible High-Speed Teleportation (Cloned Plate)
    3. No Directed Path / Topological Inconsistency
    4. Low OCR Confidence Sighting
    5. Same Camera Repeat / Stationary Sighting
    """

    @classmethod
    async def get_scenarios(cls, db: AsyncSession) -> List[GhostPlateScenario]:
        base_time = datetime(2026, 8, 27, 10, 0, 0, tzinfo=timezone.utc)
        scenarios: List[GhostPlateScenario] = []

        # 1. Normal Movement: CAM_PUN_001 -> CAM_PUN_002 (450m in 180s)
        s1_a = PlateSighting(
            plate_number="MH12AB1234",
            camera_id="CAM_PUN_001",
            timestamp=base_time,
            ocr_confidence=0.96,
            vehicle_color="white",
            vehicle_type="sedan",
        )
        s1_b = PlateSighting(
            plate_number="MH12AB1234",
            camera_id="CAM_PUN_002",
            timestamp=base_time + timedelta(seconds=180),
            ocr_confidence=0.94,
            vehicle_color="white",
            vehicle_type="sedan",
        )
        alert_1 = await GhostPlateDetector.analyze_sighting_pair(s1_a, s1_b, db)
        scenarios.append(
            GhostPlateScenario(
                scenario_id="scenario_normal_transit",
                title="1. Normal Feasible Transit (Deccan -> FC Road)",
                description="Vehicle MH12AB1234 moving along directed corridor in 180s (realistic 9 km/h city speed).",
                expected_classification="NO_ANOMALY",
                expected_severity="NONE",
                alert=alert_1
            )
        )

        # 2. Impossible High-Speed: CAM_PUN_001 -> CAM_PUN_010 (5.8km in 8s -> 2610 km/h)
        s2_a = PlateSighting(
            plate_number="MH12AB1234",
            camera_id="CAM_PUN_001",
            timestamp=base_time,
            ocr_confidence=0.98,
            vehicle_color="white",
            vehicle_type="sedan",
        )
        s2_b = PlateSighting(
            plate_number="MH12AB1234",
            camera_id="CAM_PUN_010",
            timestamp=base_time + timedelta(seconds=8),
            ocr_confidence=0.97,
            vehicle_color="black",
            vehicle_type="suv",
        )
        alert_2 = await GhostPlateDetector.analyze_sighting_pair(s2_a, s2_b, db)
        scenarios.append(
            GhostPlateScenario(
                scenario_id="scenario_impossible_speed_clone",
                title="2. Impossible Speed / Cloned Plate Sighting",
                description="Plate MH12AB1234 sighted across 5.8 km in only 8s (2610 km/h required) + vehicle color mismatch.",
                expected_classification="POSSIBLE_CLONED_PLATE",
                expected_severity="CRITICAL",
                alert=alert_2
            )
        )

        # 3. No Directed Path / Topological Inconsistency
        s3_a = PlateSighting(
            plate_number="MH14EF9900",
            camera_id="CAM_PUN_015",
            timestamp=base_time,
            ocr_confidence=0.95,
            vehicle_color="silver",
            vehicle_type="hatchback",
        )
        s3_b = PlateSighting(
            plate_number="MH14EF9900",
            camera_id="CAM_PUN_001",
            timestamp=base_time + timedelta(seconds=300),
            ocr_confidence=0.92,
            vehicle_color="silver",
            vehicle_type="hatchback",
        )
        alert_3 = await GhostPlateDetector.analyze_sighting_pair(s3_a, s3_b, db)
        scenarios.append(
            GhostPlateScenario(
                scenario_id="scenario_topology_inconsistent",
                title="3. Topological Road Network Inconsistency",
                description="Plate MH14EF9900 observed at cameras with no valid forward directed path in the network.",
                expected_classification="TOPOLOGY_INCONSISTENT",
                expected_severity="HIGH",
                alert=alert_3
            )
        )

        # 4. Low OCR Confidence Sighting
        s4_a = PlateSighting(
            plate_number="MH12XY5500",
            camera_id="CAM_PUN_001",
            timestamp=base_time,
            ocr_confidence=0.52,
            vehicle_color="grey",
            vehicle_type="sedan",
        )
        s4_b = PlateSighting(
            plate_number="MH12XY5500",
            camera_id="CAM_PUN_004",
            timestamp=base_time + timedelta(seconds=12),
            ocr_confidence=0.48,
            vehicle_color="grey",
            vehicle_type="sedan",
        )
        alert_4 = await GhostPlateDetector.analyze_sighting_pair(s4_a, s4_b, db)
        scenarios.append(
            GhostPlateScenario(
                scenario_id="scenario_low_ocr_confidence",
                title="4. Low OCR Confidence Transition",
                description="Fast transit with low OCR confidence (52% & 48%) appropriately attenuates anomaly severity.",
                expected_classification="POSSIBLE_CLONED_PLATE",
                expected_severity="LOW",
                alert=alert_4
            )
        )

        # 5. Same Camera Repeat / Stationary Sighting
        s5_a = PlateSighting(
            plate_number="MH12AB1234",
            camera_id="CAM_PUN_001",
            timestamp=base_time,
            ocr_confidence=0.96,
            vehicle_color="white",
            vehicle_type="sedan",
        )
        s5_b = PlateSighting(
            plate_number="MH12AB1234",
            camera_id="CAM_PUN_001",
            timestamp=base_time + timedelta(seconds=120),
            ocr_confidence=0.95,
            vehicle_color="white",
            vehicle_type="sedan",
        )
        alert_5 = await GhostPlateDetector.analyze_sighting_pair(s5_a, s5_b, db)
        scenarios.append(
            GhostPlateScenario(
                scenario_id="scenario_same_camera_repeat",
                title="5. Same-Camera Stationary Observation",
                description="Repeated sighting of plate MH12AB1234 at the same camera station across 2 minutes.",
                expected_classification="NORMAL_REPEAT_SIGHTING",
                expected_severity="NONE",
                alert=alert_5
            )
        )

        return scenarios
