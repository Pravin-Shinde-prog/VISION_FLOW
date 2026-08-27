from datetime import datetime, timezone, timedelta
from typing import List
from app.graph.builder import DirectedRoadGraph
from app.graph.validator import TransitionValidator
from app.graph.schemas import (
    TransitionValidationRequest,
    GraphDemoScenario,
)


class GraphDemoScenarios:
    """
    Pre-configured reproducible test scenarios showcasing Spatio-Temporal Graph Engine capabilities:
    1. Realistic Feasible Urban Transit
    2. Physically Impossible High-Speed Movement (TOO_FAST)
    3. Severe Traffic Congestion / Delay (TOO_SLOW)
    4. Topologically Disconnected Cameras (NO_FEASIBLE_PATH)
    """

    @classmethod
    def get_scenarios(cls, graph: DirectedRoadGraph) -> List[GraphDemoScenario]:
        base_time = datetime(2026, 8, 27, 10, 0, 0, tzinfo=timezone.utc)
        scenarios: List[GraphDemoScenario] = []

        # 1. Feasible Urban Transit (CAM_PUN_001 -> CAM_PUN_002, 450m in 65s -> 25 km/h)
        req_1 = TransitionValidationRequest(
            source_camera_id="CAM_PUN_001",
            target_camera_id="CAM_PUN_002",
            source_timestamp=base_time,
            target_timestamp=base_time + timedelta(seconds=65),
            plate_number="MH12AB1234",
            reid_confidence=0.95,
        )
        res_1 = TransitionValidator.validate_transition(graph, req_1)
        scenarios.append(
            GraphDemoScenario(
                scenario_id="scenario_feasible_corridor",
                title="Realistic Feasible Transit (Deccan -> FC Road)",
                description="Standard city vehicle moving along directed corridor CAM_PUN_001 -> CAM_PUN_002 in 65s.",
                source_camera_id="CAM_PUN_001",
                target_camera_id="CAM_PUN_002",
                source_time="10:00:00",
                target_time="10:01:05",
                observed_delta_seconds=65.0,
                expected_status="TEMPORALLY_FEASIBLE",
                category="FEASIBLE",
                validation_result=res_1
            )
        )

        # 2. Impossible High-Speed Movement (CAM_PUN_001 -> CAM_PUN_004, 3.2km in 8s -> 1440 km/h)
        req_2 = TransitionValidationRequest(
            source_camera_id="CAM_PUN_001",
            target_camera_id="CAM_PUN_004",
            source_timestamp=base_time,
            target_timestamp=base_time + timedelta(seconds=8),
            plate_number="MH12AB1234",
            reid_confidence=0.88,
        )
        res_2 = TransitionValidator.validate_transition(graph, req_2)
        scenarios.append(
            GraphDemoScenario(
                scenario_id="scenario_too_fast_impossible",
                title="Impossible High-Speed Transition (Deccan -> University)",
                description="Sightings separated by 3.2 km recorded only 8 seconds apart (requires 1440 km/h average speed).",
                source_camera_id="CAM_PUN_001",
                target_camera_id="CAM_PUN_004",
                source_time="10:00:00",
                target_time="10:00:08",
                observed_delta_seconds=8.0,
                expected_status="TOO_FAST",
                category="TOO_FAST",
                validation_result=res_2
            )
        )

        # 3. Severe Congestion / Extended Delay (CAM_PUN_001 -> CAM_PUN_002, 450m in 1800s / 30 mins)
        req_3 = TransitionValidationRequest(
            source_camera_id="CAM_PUN_001",
            target_camera_id="CAM_PUN_002",
            source_timestamp=base_time,
            target_timestamp=base_time + timedelta(seconds=1800),
            plate_number="MH12AB1234",
            reid_confidence=0.82,
            congestion_tolerance_factor=2.0
        )
        res_3 = TransitionValidator.validate_transition(graph, req_3)
        scenarios.append(
            GraphDemoScenario(
                scenario_id="scenario_congestion_too_slow",
                title="Extreme Congestion / Extended Stop (Deccan -> FC Road)",
                description="Vehicle observed 30 minutes later across a 450m link, exceeding reasonable travel bounds.",
                source_camera_id="CAM_PUN_001",
                target_camera_id="CAM_PUN_002",
                source_time="10:00:00",
                target_time="10:30:00",
                observed_delta_seconds=1800.0,
                expected_status="TOO_SLOW",
                category="CONGESTION",
                validation_result=res_3
            )
        )

        # 4. Topologically Disconnected Nodes / Reverse on One-Way
        # CAM_PUN_004 to CAM_PUN_001 if no direct backward road exists
        req_4 = TransitionValidationRequest(
            source_camera_id="CAM_PUN_015",
            target_camera_id="CAM_PUN_001",
            source_timestamp=base_time,
            target_timestamp=base_time + timedelta(seconds=300),
            plate_number="MH12AB1234",
            reid_confidence=0.75,
        )
        res_4 = TransitionValidator.validate_transition(graph, req_4)
        scenarios.append(
            GraphDemoScenario(
                scenario_id="scenario_no_path_topological",
                title="Topologically Disconnected / Opposite Flow",
                description="Querying cameras with no directed path in the road graph verifies strict directionality enforcement.",
                source_camera_id="CAM_PUN_015",
                target_camera_id="CAM_PUN_001",
                source_time="10:00:00",
                target_time="10:05:00",
                observed_delta_seconds=300.0,
                expected_status=res_4.status,
                category="NO_PATH" if not res_4.path_exists else "FEASIBLE",
                validation_result=res_4
            )
        )

        return scenarios
