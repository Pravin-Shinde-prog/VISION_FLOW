import time
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.anpr.normalizer import IndianPlateNormalizer
from app.ghost_plates.schemas import (
    PlateSighting,
    GhostPlateAlertRecord,
    GhostPlateAnalysisRequest,
    LiveSightingEvaluationRequest,
    LiveSightingEvaluationResponse,
    GhostPlateScenario,
    GhostPlateStatusUpdate,
)
from app.ghost_plates.detector import GhostPlateDetector
from app.ghost_plates.demo_scenarios import GhostPlateDemoScenarios
from app.models.ghost_plate import GhostPlateAlert
from app.models.detection import Detection
from app.models.camera import Camera


class GhostPlateEngine:
    """
    High-level engine for Ghost / Cloned Plate anomaly detection,
    database persistence, alert queries, and operator review lifecycle.
    """

    @classmethod
    async def analyze_transition(
        cls,
        req: GhostPlateAnalysisRequest,
        db: AsyncSession
    ) -> GhostPlateAlertRecord:
        return await GhostPlateDetector.analyze_sighting_pair(
            req.source_sighting,
            req.target_sighting,
            db,
            congestion_tolerance=req.congestion_tolerance_factor
        )

    @classmethod
    async def evaluate_live_sighting(
        cls,
        req: LiveSightingEvaluationRequest,
        db: AsyncSession
    ) -> LiveSightingEvaluationResponse:
        start_time = time.perf_counter()

        normalizer = IndianPlateNormalizer()
        norm_res = normalizer.normalize(req.sighting.plate_number)
        norm_plate = norm_res.normalized_plate or req.sighting.plate_number.replace(" ", "").upper()
        window_start = req.sighting.timestamp - timedelta(minutes=req.history_window_minutes)

        # Search previous sightings with matching normalized plate in detections table
        query = (
            select(Detection)
            .join(Camera, Detection.camera_id == Camera.id)
            .where(
                and_(
                    Detection.plate_number.isnot(None),
                    Detection.timestamp >= window_start,
                    Detection.timestamp <= req.sighting.timestamp + timedelta(seconds=10),
                )
            )
            .order_by(Detection.timestamp.desc())
            .limit(20)
        )

        res = await db.execute(query)
        recent_detections = res.scalars().all()

        alerts_generated: List[GhostPlateAlertRecord] = []
        highest_score = 0.0

        for det in recent_detections:
            if not det.plate_number or not det.camera:
                continue
            cand_res = normalizer.normalize(det.plate_number)
            cand_norm = cand_res.normalized_plate or det.plate_number.replace(" ", "").upper()
            if cand_norm != norm_plate:
                continue

            prev_sighting = PlateSighting(
                plate_number=det.plate_number,
                camera_id=det.camera.camera_id,
                timestamp=det.timestamp,
                detection_id=det.id,
                ocr_confidence=det.ocr_confidence or 0.85,
                vehicle_color=det.vehicle_color or "unknown",
                vehicle_type=det.vehicle_type or "unknown",
                snapshot_path=det.snapshot_path,
            )

            # Analyze pair
            alert_rec = await GhostPlateDetector.analyze_sighting_pair(prev_sighting, req.sighting, db)

            if alert_rec.anomaly_score > 0.40 and alert_rec.alert_type in ("POSSIBLE_CLONED_PLATE", "TOPOLOGY_INCONSISTENT"):
                alerts_generated.append(alert_rec)
                highest_score = max(highest_score, alert_rec.anomaly_score)

                # Persist alert to database
                db_alert = GhostPlateAlert(
                    alert_uid=alert_rec.alert_id,
                    plate_number=alert_rec.plate_number,
                    normalized_plate=alert_rec.normalized_plate,
                    alert_type=alert_rec.alert_type,
                    severity=alert_rec.severity,
                    status="NEW",
                    source_camera_id=alert_rec.source_camera_id,
                    target_camera_id=alert_rec.target_camera_id,
                    source_timestamp=alert_rec.source_timestamp,
                    target_timestamp=alert_rec.target_timestamp,
                    observed_delta_seconds=alert_rec.observed_delta_seconds,
                    minimum_feasible_time_seconds=alert_rec.minimum_feasible_time_seconds,
                    distance_meters=alert_rec.distance_meters,
                    required_speed_kmh=alert_rec.required_speed_kmh,
                    speed_limit_kmh=alert_rec.speed_limit_kmh,
                    graph_status=alert_rec.graph_status,
                    anomaly_score=alert_rec.anomaly_score,
                    explanation=alert_rec.explanation,
                    evidence_data={"checklist": [e.model_dump() for e in alert_rec.evidence_checklist]},
                    source_snapshot_ref=alert_rec.source_snapshot_ref,
                    target_snapshot_ref=alert_rec.target_snapshot_ref,
                    created_at=datetime.now(timezone.utc),
                )
                db.add(db_alert)

        if alerts_generated:
            await db.commit()

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return LiveSightingEvaluationResponse(
            evaluated_sighting=req.sighting,
            previous_sightings_found=len(recent_detections),
            alerts_generated=alerts_generated,
            is_suspicious=len(alerts_generated) > 0,
            highest_anomaly_score=highest_score,
            execution_latency_ms=latency_ms
        )

    @classmethod
    async def list_alerts(
        cls,
        db: AsyncSession,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        plate_number: Optional[str] = None,
        limit: int = 50
    ) -> List[GhostPlateAlertRecord]:
        query = select(GhostPlateAlert).order_by(GhostPlateAlert.created_at.desc())

        if severity:
            query = query.where(GhostPlateAlert.severity == severity.upper())
        if status:
            query = query.where(GhostPlateAlert.status == status.upper())
        if plate_number:
            normalizer = IndianPlateNormalizer()
            norm = normalizer.normalize(plate_number).normalized_plate or plate_number.replace(" ", "").upper()
            query = query.where(GhostPlateAlert.normalized_plate == norm)

        query = query.limit(limit)
        res = await db.execute(query)
        db_alerts = res.scalars().all()

        records: List[GhostPlateAlertRecord] = []
        for a in db_alerts:
            evidence_items = []
            if a.evidence_data and "checklist" in a.evidence_data:
                from app.ghost_plates.schemas import EvidenceItem
                evidence_items = [EvidenceItem(**item) for item in a.evidence_data["checklist"]]

            records.append(
                GhostPlateAlertRecord(
                    alert_id=a.alert_uid,
                    plate_number=a.plate_number,
                    normalized_plate=a.normalized_plate,
                    alert_type=a.alert_type,
                    severity=a.severity,
                    status=a.status,
                    source_camera_id=a.source_camera_id,
                    target_camera_id=a.target_camera_id,
                    source_timestamp=a.source_timestamp,
                    target_timestamp=a.target_timestamp,
                    observed_delta_seconds=a.observed_delta_seconds,
                    minimum_feasible_time_seconds=a.minimum_feasible_time_seconds,
                    distance_meters=a.distance_meters,
                    required_speed_kmh=a.required_speed_kmh,
                    speed_limit_kmh=a.speed_limit_kmh,
                    graph_status=a.graph_status,
                    anomaly_score=a.anomaly_score,
                    ocr_confidence_product=0.95,
                    reid_similarity_score=None,
                    evidence_checklist=evidence_items,
                    explanation=a.explanation,
                    source_snapshot_ref=a.source_snapshot_ref or "/snapshots/sim_src.jpg",
                    target_snapshot_ref=a.target_snapshot_ref or "/snapshots/sim_dst.jpg",
                    is_simulated=True,
                    created_at=a.created_at,
                    analysis_latency_ms=0.5
                )
            )

        return records

    @classmethod
    async def update_alert_status(
        cls,
        alert_id: str,
        update_data: GhostPlateStatusUpdate,
        db: AsyncSession
    ) -> Optional[GhostPlateAlertRecord]:
        query = select(GhostPlateAlert).where(GhostPlateAlert.alert_uid == alert_id)
        res = await db.execute(query)
        alert = res.scalars().first()
        if not alert:
            return None

        alert.status = update_data.status
        alert.operator_notes = update_data.notes
        alert.reviewed_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(alert)

        evidence_items = []
        if alert.evidence_data and "checklist" in alert.evidence_data:
            from app.ghost_plates.schemas import EvidenceItem
            evidence_items = [EvidenceItem(**item) for item in alert.evidence_data["checklist"]]

        return GhostPlateAlertRecord(
            alert_id=alert.alert_uid,
            plate_number=alert.plate_number,
            normalized_plate=alert.normalized_plate,
            alert_type=alert.alert_type,
            severity=alert.severity,
            status=alert.status,
            source_camera_id=alert.source_camera_id,
            target_camera_id=alert.target_camera_id,
            source_timestamp=alert.source_timestamp,
            target_timestamp=alert.target_timestamp,
            observed_delta_seconds=alert.observed_delta_seconds,
            minimum_feasible_time_seconds=alert.minimum_feasible_time_seconds,
            distance_meters=alert.distance_meters,
            required_speed_kmh=alert.required_speed_kmh,
            speed_limit_kmh=alert.speed_limit_kmh,
            graph_status=alert.graph_status,
            anomaly_score=alert.anomaly_score,
            ocr_confidence_product=0.95,
            reid_similarity_score=None,
            evidence_checklist=evidence_items,
            explanation=alert.explanation,
            source_snapshot_ref=alert.source_snapshot_ref or "/snapshots/sim_src.jpg",
            target_snapshot_ref=alert.target_snapshot_ref or "/snapshots/sim_dst.jpg",
            is_simulated=True,
            created_at=alert.created_at,
            analysis_latency_ms=0.5
        )

    @classmethod
    async def get_demo_scenarios(cls, db: AsyncSession) -> List[GhostPlateScenario]:
        return await GhostPlateDemoScenarios.get_scenarios(db)
