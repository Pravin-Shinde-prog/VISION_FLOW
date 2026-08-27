import base64
import cv2
import numpy as np
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from app.edge_vision.schemas import (
    EdgeVisionProcessResponse,
    PreprocessingConfig,
    CandidatePlateRegion,
    PlateAnomalyFlags,
)
from app.edge_vision.preprocessing import ImagePreprocessor
from app.edge_vision.quality import ImageQualityAnalyzer
from app.edge_vision.plate_detector import PlateRegionDetector
from app.edge_vision.plate_analysis import PlateQualityAndAnomalyAnalyzer


class EdgeVisionPipeline:
    """
    Main orchestrator for the Stage 8 Smart Edge Vision & Plate Preprocessing pipeline:
    1. Resizes and enhances raw input frame (CLAHE, glare/shadow compensation, unsharp sharpening).
    2. Measures frame-level image quality metrics (brightness, contrast, sharpness, glare, uniformity).
    3. Detects candidate license plate regions with geometric & gradient heuristics.
    4. Evaluates localized plate quality and rule-based physical anomaly/compliance flags.
    5. Formats normalized edge metadata and base64 preview overlays for the dashboard.
    """

    def __init__(self, config: Optional[PreprocessingConfig] = None):
        self.config = config or PreprocessingConfig()
        self.preprocessor = ImagePreprocessor(self.config)
        self.quality_analyzer = ImageQualityAnalyzer()
        self.plate_detector = PlateRegionDetector()
        self.plate_analyzer = PlateQualityAndAnomalyAnalyzer()

    def process_image(
        self,
        bgr_image: np.ndarray,
        camera_id: Optional[str] = None
    ) -> EdgeVisionProcessResponse:
        start_time = time.perf_counter()

        orig_h, orig_w = bgr_image.shape[:2]

        # 1. Resize if required
        resized_frame, scale = self.preprocessor.resize_if_needed(bgr_image)
        proc_h, proc_w = resized_frame.shape[:2]

        # 2. Image Enhancement
        enhanced_frame = self.preprocessor.enhance_frame(resized_frame)
        gray_enhanced = cv2.cvtColor(enhanced_frame, cv2.COLOR_BGR2GRAY)

        # 3. Quality Metrics Evaluation
        quality_metrics = self.quality_analyzer.analyze(enhanced_frame)

        # 4. Extract High-Contrast Edge Representation
        edge_map = self.preprocessor.extract_edge_representation(gray_enhanced)

        # 5. Locate Candidate Plate Regions
        raw_candidates = self.plate_detector.detect_candidate_regions(enhanced_frame)

        candidate_plates = []
        annotated_preview = enhanced_frame.copy()

        for idx, candidate in enumerate(raw_candidates, start=1):
            plate_result = self.plate_analyzer.analyze_plate_region(
                region_id=idx,
                candidate=candidate,
                full_image=enhanced_frame
            )

            # Crop base64 encoding
            crop_bgr = candidate["cropped_bgr"]
            _, crop_buffer = cv2.imencode(".jpg", crop_bgr, [cv2.IMWRITE_JPEG_QUALITY, 90])
            crop_b64 = base64.b64encode(crop_buffer).decode("utf-8")
            plate_result.cropped_plate_b64 = crop_b64

            candidate_plates.append(plate_result)

            # Draw bounding box and label on preview
            x1, y1, x2, y2 = plate_result.bbox
            color = (0, 220, 100) if plate_result.condition == "NORMAL" else (0, 160, 255)
            cv2.rectangle(annotated_preview, (x1, y1), (x2, y2), color, 2)
            label = f"PLATE {idx}: {plate_result.condition} ({int(plate_result.plate_quality_score * 100)}%)"
            cv2.putText(annotated_preview, label, (x1, max(18, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # 6. Overall State Determination
        plate_detected = len(candidate_plates) > 0
        primary_plate = candidate_plates[0] if plate_detected else None

        if not plate_detected:
            summary_condition = "MISSING"
            overall_anomaly = True
            # Create a missing plate candidate stub for reporting
            missing_flags = PlateAnomalyFlags(
                missing_plate=True,
                broken_plate=False,
                damaged_plate=False,
                modified_plate=False,
                non_standard_plate=False,
                obscured_plate=False,
                unreadable_plate=True
            )
        else:
            summary_condition = primary_plate.condition
            overall_anomaly = summary_condition != "NORMAL"

        # 7. Encode preview and edge maps to JPEG base64
        _, preview_buffer = cv2.imencode(".jpg", annotated_preview, [cv2.IMWRITE_JPEG_QUALITY, 85])
        enhanced_b64 = base64.b64encode(preview_buffer).decode("utf-8")

        _, edge_buffer = cv2.imencode(".jpg", edge_map, [cv2.IMWRITE_JPEG_QUALITY, 80])
        edge_b64 = base64.b64encode(edge_buffer).decode("utf-8")

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return EdgeVisionProcessResponse(
            data_source="edge_vision",
            pipeline_version="edge_v1.0",
            processed_at=datetime.now(timezone.utc),
            camera_id=camera_id,
            frame_width=orig_w,
            frame_height=orig_h,
            processing_latency_ms=latency_ms,
            image_quality=quality_metrics,
            plate_detected=plate_detected,
            candidate_plates_count=len(candidate_plates),
            candidate_plates=candidate_plates,
            primary_plate=primary_plate,
            overall_anomaly_detected=overall_anomaly,
            summary_condition=summary_condition,
            enhanced_frame_b64=enhanced_b64,
            edge_representation_b64=edge_b64
        )
