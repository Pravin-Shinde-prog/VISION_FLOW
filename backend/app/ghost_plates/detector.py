import time
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.anpr.normalizer import IndianPlateNormalizer
from app.graph.engine import SpatioTemporalGraphEngine
from app.graph.schemas import TransitionValidationRequest
from app.reid.similarity import ReIDSimilarityCalculator
from app.reid.schemas import VehicleVisualSignature
from app.ghost_plates.schemas import (
    PlateSighting,
    GhostPlateAlertRecord,
    EvidenceItem,
)
from app.ghost_plates.evaluator import GhostPlateEvaluator
from app.models.detection import Detection
from app.models.camera import Camera


class GhostPlateDetector:
    """
    Coordinates ANPR plate normalization, Spatio-Temporal Graph path kinematics,
    and Re-ID cross-checking to detect cloned / ghost plate anomalies.
    """

    @classmethod
    async def analyze_sighting_pair(
        cls,
        sighting_a: PlateSighting,
        sighting_b: PlateSighting,
        db: AsyncSession,
        congestion_tolerance: float = 3.5
    ) -> GhostPlateAlertRecord:
        start_time = time.perf_counter()

        # 1. Normalize Plate Strings
        normalizer = IndianPlateNormalizer()
        res_a = normalizer.normalize(sighting_a.plate_number)
        res_b = normalizer.normalize(sighting_b.plate_number)
        norm_a = res_a.normalized_plate or sighting_a.plate_number.replace(" ", "").upper()
        norm_b = res_b.normalized_plate or sighting_b.plate_number.replace(" ", "").upper()

        # Ensure chronological ordering (source -> target)
        if sighting_a.timestamp <= sighting_b.timestamp:
            src, dst = sighting_a, sighting_b
        else:
            src, dst = sighting_b, sighting_a

        # 2. Spatio-Temporal Graph Validation
        t_req = TransitionValidationRequest(
            source_camera_id=src.camera_id,
            target_camera_id=dst.camera_id,
            source_timestamp=src.timestamp,
            target_timestamp=dst.timestamp,
            plate_number=norm_a,
            reid_confidence=None,
            congestion_tolerance_factor=congestion_tolerance
        )
        graph_res = await SpatioTemporalGraphEngine.validate_transition(t_req, db)

        # 3. Vehicle Re-ID Cross-Check if visual features present
        reid_sim: Optional[float] = None
        if src.vehicle_color and dst.vehicle_color and src.vehicle_color != "unknown":
            sig_src = VehicleVisualSignature(
                vehicle_color=src.vehicle_color,
                vehicle_type=src.vehicle_type or "unknown",
                aspect_ratio=src.aspect_ratio or 1.5,
                distinctive_features=[],
                plate_number=norm_a,
            )
            sig_dst = VehicleVisualSignature(
                vehicle_color=dst.vehicle_color,
                vehicle_type=dst.vehicle_type or "unknown",
                aspect_ratio=dst.aspect_ratio or 1.5,
                distinctive_features=[],
                plate_number=norm_b,
            )
            reid_match = ReIDSimilarityCalculator.calculate_similarity(sig_src, sig_dst)
            reid_sim = reid_match.overall_score

        # 4. Forensic Anomaly Evaluation
        alert_type, severity, anomaly_score, evidence_list, explanation = GhostPlateEvaluator.evaluate_anomaly(
            plate_normalized=norm_a,
            source_camera_id=src.camera_id,
            target_camera_id=dst.camera_id,
            ocr_conf_source=src.ocr_confidence,
            ocr_conf_target=dst.ocr_confidence,
            graph_status=graph_res.status,
            observed_delta_seconds=graph_res.observed_delta_seconds,
            minimum_feasible_time_seconds=graph_res.minimum_time_seconds,
            distance_meters=graph_res.distance_meters,
            required_speed_kmh=graph_res.required_average_speed_kmh,
            speed_limit_kmh=graph_res.speed_limit_kmh,
            reid_similarity=reid_sim
        )

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        alert_id = f"GHOST_{uuid.uuid4().hex[:8].upper()}"

        return GhostPlateAlertRecord(
            alert_id=alert_id,
            plate_number=sighting_a.plate_number,
            normalized_plate=norm_a,
            alert_type=alert_type,
            severity=severity,
            status="NEW",
            source_camera_id=src.camera_id,
            target_camera_id=dst.camera_id,
            source_timestamp=src.timestamp,
            target_timestamp=dst.timestamp,
            observed_delta_seconds=graph_res.observed_delta_seconds,
            minimum_feasible_time_seconds=graph_res.minimum_time_seconds,
            distance_meters=graph_res.distance_meters,
            required_speed_kmh=graph_res.required_average_speed_kmh,
            speed_limit_kmh=graph_res.speed_limit_kmh,
            graph_status=graph_res.status,
            anomaly_score=anomaly_score,
            ocr_confidence_product=round(src.ocr_confidence * dst.ocr_confidence, 3),
            reid_similarity_score=reid_sim,
            evidence_checklist=evidence_list,
            explanation=explanation,
            source_snapshot_ref=src.snapshot_path or f"/snapshots/sim_{src.camera_id}_{norm_a}.jpg [SIMULATED]",
            target_snapshot_ref=dst.snapshot_path or f"/snapshots/sim_{dst.camera_id}_{norm_a}.jpg [SIMULATED]",
            is_simulated=True,
            created_at=datetime.now(timezone.utc),
            analysis_latency_ms=latency_ms
        )
