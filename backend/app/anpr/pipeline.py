import base64
import time
import cv2
import numpy as np
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.edge_vision.pipeline import EdgeVisionPipeline
from app.edge_vision.schemas import PreprocessingConfig
from app.anpr.schemas import (
    ANPRProcessResponse,
    ANPRCandidateResult,
    PlateOCRResult,
)
from app.anpr.engine import PlateOCREngine
from app.models.detection import Detection
from app.models.camera import Camera
from sqlalchemy import select


class ANPRPipeline:
    """
    End-to-End Automatic Number Plate Recognition (ANPR) Pipeline:
    Camera Image -> Edge Preprocessing -> Plate Detection -> Plate Crop ->
    OCR Character Extraction -> Positional Normalization -> Indian Format Validation ->
    Multi-Candidate Ranking -> Normalized Detection Metadata.
    """

    def __init__(self, config: Optional[PreprocessingConfig] = None):
        self.edge_pipeline = EdgeVisionPipeline(config)
        self.ocr_engine = PlateOCREngine()

    async def process_frame(
        self,
        bgr_image: np.ndarray,
        camera_id: Optional[str] = None,
        db_session: Optional[AsyncSession] = None,
        persist: bool = False
    ) -> ANPRProcessResponse:
        start_time = time.perf_counter()

        # 1. Execute Stage 8 Edge Vision & Plate Detection
        edge_start = time.perf_counter()
        edge_res = self.edge_pipeline.process_image(bgr_image, camera_id=camera_id)
        edge_latency = round((time.perf_counter() - edge_start) * 1000, 2)

        # 2. Run OCR on each candidate plate crop
        ocr_start = time.perf_counter()
        anpr_candidates: List[ANPRCandidateResult] = []

        annotated_preview = bgr_image.copy()

        for cand in edge_res.candidate_plates:
            # Decode crop from candidate bounding box
            x1, y1, x2, y2 = cand.bbox
            crop_bgr = bgr_image[y1:y2, x1:x2]

            ocr_result = self.ocr_engine.recognize_plate(
                plate_crop_bgr=crop_bgr,
                plate_quality=cand.plate_quality_score
            )

            # Calculate multi-candidate composite rank score
            # Rank score = 0.45 * OCR final conf + 0.35 * detector conf + 0.20 * plate quality
            rank_score = round(
                0.45 * ocr_result.final_confidence +
                0.35 * cand.confidence +
                0.20 * cand.plate_quality_score,
                3
            )

            anpr_cand = ANPRCandidateResult(
                region_id=cand.region_id,
                bbox=cand.bbox,
                confidence=cand.confidence,
                aspect_ratio=cand.aspect_ratio,
                plate_quality_score=cand.plate_quality_score,
                condition=cand.condition,
                anomaly_flags=cand.anomaly_flags,
                ocr_result=ocr_result,
                rank_score=rank_score,
                cropped_plate_b64=cand.cropped_plate_b64
            )
            anpr_candidates.append(anpr_cand)

            # Draw visual bounding box and recognized plate tag on annotated preview
            box_color = (0, 220, 100) if ocr_result.format_valid else (0, 160, 255)
            cv2.rectangle(annotated_preview, (x1, y1), (x2, y2), box_color, 2)

            plate_tag = ocr_result.normalized_plate or "NO_OCR"
            tag_label = f"[{plate_tag}] {int(ocr_result.final_confidence * 100)}%"
            cv2.putText(annotated_preview, tag_label, (x1, max(20, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, box_color, 2)

        ocr_latency = round((time.perf_counter() - ocr_start) * 1000, 2)

        # 3. Sort and select primary candidate plate
        anpr_candidates.sort(key=lambda c: c.rank_score, reverse=True)
        primary_plate = anpr_candidates[0] if anpr_candidates else None

        # 4. Overall Condition & Detection flag
        plate_detected = len(anpr_candidates) > 0
        summary_condition = primary_plate.condition if primary_plate else "MISSING"

        # Encode annotated preview to base64 JPEG
        _, preview_buf = cv2.imencode(".jpg", annotated_preview, [cv2.IMWRITE_JPEG_QUALITY, 85])
        annotated_b64 = base64.b64encode(preview_buf).decode("utf-8")

        total_latency = round((time.perf_counter() - start_time) * 1000, 2)

        persisted_id: Optional[int] = None

        # 5. Optional Database Persistence
        if persist and db_session is not None and primary_plate is not None:
            persisted_id = await self._persist_anpr_detection(
                db_session=db_session,
                camera_code=camera_id or "CAM_PUN_001",
                primary_plate=primary_plate,
                total_latency=total_latency
            )

        return ANPRProcessResponse(
            data_source="anpr_engine",
            pipeline_version="anpr_v1.0",
            processed_at=datetime.now(timezone.utc),
            camera_id=camera_id,
            frame_width=edge_res.frame_width,
            frame_height=edge_res.frame_height,
            total_latency_ms=total_latency,
            edge_vision_latency_ms=edge_latency,
            ocr_latency_ms=ocr_latency,
            plate_detected=plate_detected,
            primary_plate=primary_plate,
            all_candidates=anpr_candidates,
            image_quality=edge_res.image_quality,
            summary_condition=summary_condition,
            annotated_frame_b64=annotated_b64,
            cropped_plate_b64=primary_plate.cropped_plate_b64 if primary_plate else None,
            persisted_detection_id=persisted_id
        )

    async def _persist_anpr_detection(
        self,
        db_session: AsyncSession,
        camera_code: str,
        primary_plate: ANPRCandidateResult,
        total_latency: float
    ) -> Optional[int]:
        """Persists successful ANPR sighting into PostgreSQL detections table."""
        try:
            cam_q = await db_session.execute(select(Camera).where(Camera.camera_id == camera_code.upper()))
            camera = cam_q.scalars().first()
            if not camera:
                return None

            ocr_res = primary_plate.ocr_result
            import uuid
            uid = f"evt_anpr_{uuid.uuid4().hex[:12]}"

            det = Detection(
                detection_uid=uid,
                camera_id=camera.id,
                timestamp=datetime.now(timezone.utc),
                plate_number=ocr_res.normalized_plate,
                ocr_confidence=ocr_res.ocr_confidence,
                direction_travel="Inbound",
                snapshot_path=f"live://camera/{camera.camera_id}/anpr/{uid}.jpg",
                plate_anomaly_flags=primary_plate.anomaly_flags.model_dump(),
                processing_metadata={
                    "data_source": "anpr_engine",
                    "pipeline_version": "anpr_v1.0",
                    "ocr_engine": ocr_res.ocr_engine,
                    "final_confidence": ocr_res.final_confidence,
                    "format_valid": ocr_res.format_valid,
                    "total_latency_ms": total_latency,
                },
                association_confidence=ocr_res.final_confidence,
            )
            db_session.add(det)
            await db_session.commit()
            return det.id
        except Exception:
            await db_session.rollback()
            return None
