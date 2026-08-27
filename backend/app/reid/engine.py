import time
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.reid.schemas import (
    VehicleVisualSignature,
    ReIDMatchResult,
    ReIDObservationPayload,
    ReIDTrackCandidate,
    ReIDTrackResponse,
)
from app.reid.similarity import ReIDSimilarityCalculator
from app.reid.spatial_temporal import SpatialTemporalValidator
from app.reid.feature_extractor import VisualFeatureExtractor
from app.models.detection import Detection
from app.models.camera import Camera


class VehicleReIDEngine:
    """
    Multi-Feature Vehicle Re-Identification (Re-ID) Engine.
    Executes cross-camera visual feature matching, temporal plausibility gating,
    and explainable similarity calculation when license plates are occluded or unreadable.
    """

    def __init__(self):
        self.similarity_calc = ReIDSimilarityCalculator()
        self.spatial_temporal = SpatialTemporalValidator()
        self.feature_extractor = VisualFeatureExtractor()

    def compare_observations(
        self,
        obs_a: ReIDObservationPayload,
        obs_b: ReIDObservationPayload
    ) -> ReIDMatchResult:
        """
        Calculates explainable multi-feature similarity between two vehicle sightings.
        """
        start_time = time.perf_counter()

        # 1. Evaluate Spatial-Temporal Kinematics
        dt, dist, speed, is_plausible = self.spatial_temporal.evaluate(
            time_a=obs_a.timestamp,
            time_b=obs_b.timestamp,
            lat_a=obs_a.lat,
            lon_a=obs_a.lon,
            lat_b=obs_b.lat,
            lon_b=obs_b.lon,
        )

        # 2. Calculate Feature Similarity
        result = self.similarity_calc.calculate_similarity(
            sig_a=obs_a.signature,
            sig_b=obs_b.signature,
            delta_time_seconds=dt,
            distance_meters=dist,
            speed_kmh=speed,
            is_temporally_plausible=is_plausible
        )

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        result.reid_latency_ms = latency_ms
        return result

    async def track_vehicle_across_cameras(
        self,
        source_obs: ReIDObservationPayload,
        db_session: AsyncSession,
        time_window_minutes: int = 60,
        max_candidates: int = 10
    ) -> ReIDTrackResponse:
        """
        Searches historical camera sightings in the database and ranks candidates
        matching the source vehicle's visual signature and spatial-temporal corridor.
        """
        start_time = time.perf_counter()

        # Query recent detections
        query = select(Detection).order_by(Detection.timestamp.desc()).limit(100)
        res = await db_session.execute(query)
        db_detections = res.scalars().all()

        candidates: List[ReIDTrackCandidate] = []

        for det in db_detections:
            if det.camera is None:
                continue

            # Build candidate signature from detection metadata
            cand_sig = VehicleVisualSignature(
                vehicle_color=det.vehicle_color or "unknown",
                color_confidence=0.85,
                vehicle_type=det.vehicle_type or "unknown",
                type_confidence=0.85,
                make="unknown",
                model="unknown",
                aspect_ratio=1.5,
                distinctive_features=[],
                plate_number=det.plate_number,
                ocr_confidence=det.ocr_confidence,
            )

            cand_obs = ReIDObservationPayload(
                observation_id=det.detection_uid,
                camera_id=det.camera.camera_id,
                timestamp=det.timestamp,
                signature=cand_sig,
                lat=det.camera.latitude,
                lon=det.camera.longitude,
            )

            # Match source against candidate
            match_res = self.compare_observations(source_obs, cand_obs)

            if match_res.overall_score >= 0.40:
                candidates.append(
                    ReIDTrackCandidate(
                        candidate_id=det.detection_uid,
                        detection_id=det.id,
                        camera_id=det.camera.camera_id,
                        camera_name=det.camera.camera_name,
                        timestamp=det.timestamp,
                        plate_number=det.plate_number,
                        plate_readable=bool(det.plate_number and (det.ocr_confidence or 0.0) >= 0.50),
                        vehicle_color=det.vehicle_color or "unknown",
                        vehicle_type=det.vehicle_type or "unknown",
                        match_result=match_res
                    )
                )

        # Sort candidates descending by match score
        candidates.sort(key=lambda c: c.match_result.overall_score, reverse=True)
        top_candidates = candidates[:max_candidates]

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return ReIDTrackResponse(
            source_observation_id=source_obs.observation_id or "src_001",
            source_camera_id=source_obs.camera_id or "CAM_PUN_001",
            source_plate=source_obs.signature.plate_number,
            source_color=source_obs.signature.vehicle_color,
            source_type=source_obs.signature.vehicle_type,
            total_candidates_evaluated=len(db_detections),
            ranked_candidates=top_candidates,
            execution_latency_ms=latency_ms
        )
