import time
from datetime import datetime
from typing import Optional, List
from app.graph.builder import DirectedRoadGraph
from app.graph.pathfinding import DijkstraPathFinder
from app.graph.travel_time import TravelTimeModel
from app.graph.schemas import (
    TransitionValidationRequest,
    TransitionValidationResponse,
    SequenceValidationRequest,
    SequenceValidationResponse,
    SequenceObservation,
)


class TransitionValidator:
    """
    Validates physical and topological feasibility of vehicle transitions across cameras.
    """

    @classmethod
    def validate_transition(
        cls,
        graph: DirectedRoadGraph,
        req: TransitionValidationRequest
    ) -> TransitionValidationResponse:
        start_time = time.perf_counter()

        src = req.source_camera_id.strip().upper()
        dst = req.target_camera_id.strip().upper()

        # Calculate observed time delta
        delta_sec = abs((req.target_timestamp - req.source_timestamp).total_seconds())

        # 1. Check Pathfinding in Directed Graph G=(V,E)
        path_res = DijkstraPathFinder.find_shortest_path(graph, src, dst)

        if not path_res.path_exists:
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return TransitionValidationResponse(
                status="NO_FEASIBLE_PATH",
                source_camera_id=src,
                target_camera_id=dst,
                observed_delta_seconds=delta_sec,
                path_exists=False,
                camera_path=[],
                distance_meters=0.0,
                minimum_time_seconds=0.0,
                maximum_reasonable_time_seconds=0.0,
                required_average_speed_kmh=0.0,
                speed_limit_kmh=0.0,
                speed_ratio=0.0,
                transition_feasibility_score=0.0,
                reid_confidence=req.reid_confidence,
                explanation=f"NO_FEASIBLE_PATH: No directed road connection exists from '{src}' to '{dst}' in the Pune road network.",
                validation_latency_ms=latency_ms
            )

        # Same camera observation
        if src == dst:
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return TransitionValidationResponse(
                status="SAME_LOCATION_STATIONARY",
                source_camera_id=src,
                target_camera_id=dst,
                observed_delta_seconds=delta_sec,
                path_exists=True,
                camera_path=[src],
                distance_meters=0.0,
                minimum_time_seconds=0.0,
                maximum_reasonable_time_seconds=3600.0,
                required_average_speed_kmh=0.0,
                speed_limit_kmh=path_res.effective_speed_limit_kmh,
                speed_ratio=0.0,
                transition_feasibility_score=1.0,
                reid_confidence=req.reid_confidence,
                explanation="Vehicle observed at the same camera location across time.",
                validation_latency_ms=latency_ms
            )

        # 2. Travel Time Boundaries
        min_time = path_res.estimated_min_time_seconds
        # Congestion upper bound: scaled by user-configured tolerance factor
        max_time = path_res.estimated_max_time_seconds * (req.congestion_tolerance_factor / 3.5)

        # Kinematics
        req_speed, speed_ratio = TravelTimeModel.evaluate_kinematics(
            path_distance_meters=path_res.total_distance_meters,
            observed_delta_seconds=delta_sec,
            minimum_time_seconds=min_time,
            maximum_time_seconds=max_time,
            speed_limit_kmh=path_res.effective_speed_limit_kmh
        )

        # 3. Status Classification & Score Calculation
        # Tolerance margin: Allow up to 10% under min_time for speed tolerance
        if delta_sec < (min_time * 0.85) or speed_ratio > 1.40:
            status = "TOO_FAST"
            score = round(max(0.0, (delta_sec / max(1.0, min_time)) * 0.40), 3)
            explanation = (
                f"TOO_FAST: Observed transit time of {int(delta_sec)}s requires average speed of {req_speed} km/h "
                f"(exceeds {path_res.effective_speed_limit_kmh} km/h speed limit by {int((speed_ratio-1.0)*100)}%). "
                f"Temporally inconsistent with configured road network constraints."
            )
        elif delta_sec > max_time:
            status = "TOO_SLOW"
            score = round(max(0.20, 0.60 - 0.30 * ((delta_sec - max_time) / max(1.0, max_time))), 3)
            explanation = (
                f"TOO_SLOW: Observed transit time of {int(delta_sec)}s exceeds reasonable corridor congestion threshold "
                f"({int(max_time)}s). Likely stopped, parked, or diverted off-network."
            )
        else:
            status = "TEMPORALLY_FEASIBLE"
            score = round(1.0 if delta_sec <= min_time * 2.0 else 0.85, 3)
            explanation = (
                f"TEMPORALLY_FEASIBLE: Observed transit time of {int(delta_sec)}s over {round(path_res.total_distance_meters/1000.0, 2)} km "
                f"corridor matches realistic urban traffic flow (avg speed {req_speed} km/h, speed limit {path_res.effective_speed_limit_kmh} km/h)."
            )

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return TransitionValidationResponse(
            status=status,
            source_camera_id=src,
            target_camera_id=dst,
            observed_delta_seconds=delta_sec,
            path_exists=True,
            camera_path=path_res.camera_path,
            distance_meters=path_res.total_distance_meters,
            minimum_time_seconds=min_time,
            maximum_reasonable_time_seconds=round(max_time, 1),
            required_average_speed_kmh=req_speed,
            speed_limit_kmh=path_res.effective_speed_limit_kmh,
            speed_ratio=speed_ratio,
            transition_feasibility_score=score,
            reid_confidence=req.reid_confidence,
            explanation=explanation,
            validation_latency_ms=latency_ms
        )

    @classmethod
    def validate_sequence(
        cls,
        graph: DirectedRoadGraph,
        req: SequenceValidationRequest
    ) -> SequenceValidationResponse:
        """
        Validates consecutive legs of a multi-camera journey sequence (e.g. A -> B -> C -> D).
        """
        start_time = time.perf_counter()
        obs_list = sorted(req.observations, key=lambda o: o.timestamp)

        if len(obs_list) < 2:
            return SequenceValidationResponse(
                total_hops=0,
                feasible_hops=0,
                anomalous_hops=0,
                overall_route_feasible=True,
                transitions=[],
                summary_explanation="At least two consecutive observations required to validate a route sequence.",
                execution_latency_ms=0.0
            )

        transitions: List[TransitionValidationResponse] = []
        feasible_count = 0
        anomalous_count = 0

        for i in range(len(obs_list) - 1):
            src_obs = obs_list[i]
            dst_obs = obs_list[i + 1]

            t_req = TransitionValidationRequest(
                source_camera_id=src_obs.camera_id,
                target_camera_id=dst_obs.camera_id,
                source_timestamp=src_obs.timestamp,
                target_timestamp=dst_obs.timestamp,
                vehicle_id=src_obs.observation_id,
                plate_number=src_obs.plate_number,
                reid_confidence=dst_obs.reid_confidence,
                congestion_tolerance_factor=req.congestion_tolerance_factor
            )

            res = cls.validate_transition(graph, t_req)
            transitions.append(res)

            if res.status in ("TEMPORALLY_FEASIBLE", "SAME_LOCATION_STATIONARY"):
                feasible_count += 1
            else:
                anomalous_count += 1

        overall_feasible = anomalous_count == 0
        total_hops = len(transitions)

        if overall_feasible:
            summary = f"All {total_hops} movement legs physically and topologically valid across the Pune road network."
        else:
            summary = f"Route flagged with {anomalous_count} anomalous transition(s) out of {total_hops} legs."

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return SequenceValidationResponse(
            total_hops=total_hops,
            feasible_hops=feasible_count,
            anomalous_hops=anomalous_count,
            overall_route_feasible=overall_feasible,
            transitions=transitions,
            summary_explanation=summary,
            execution_latency_ms=latency_ms
        )
