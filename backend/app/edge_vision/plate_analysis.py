import cv2
import numpy as np
from typing import Dict, Any, Tuple
from app.edge_vision.schemas import PlateAnomalyFlags, CandidatePlateRegion
from app.edge_vision.quality import ImageQualityAnalyzer


class PlateQualityAndAnomalyAnalyzer:
    """
    Evaluates localized license plate crop quality and assesses rule-based physical integrity / compliance.
    Classifies condition into: NORMAL, PARTIAL, OCCLUDED, DAMAGED, UNREADABLE.
    """

    def __init__(self):
        self.quality_analyzer = ImageQualityAnalyzer()

    def analyze_plate_region(
        self,
        region_id: int,
        candidate: Dict[str, Any],
        full_image: np.ndarray
    ) -> CandidatePlateRegion:
        crop: np.ndarray = candidate["cropped_bgr"]
        bbox = candidate["bbox"]
        aspect_ratio = candidate["aspect_ratio"]
        confidence = candidate["confidence"]

        if len(crop.shape) == 3:
            gray_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        else:
            gray_crop = crop

        # 1. Compute Quality Metrics on Plate Crop
        brightness = self.quality_analyzer.compute_brightness_score(gray_crop)
        contrast = self.quality_analyzer.compute_contrast_score(gray_crop)
        sharpness = self.quality_analyzer.compute_sharpness_score(gray_crop)
        
        # On a license plate, a white background is normal.
        # Glare is defined as overexposure where text is washed out (low contrast + high saturation).
        saturated_pixels = np.count_nonzero(gray_crop >= 252)
        sat_ratio = saturated_pixels / float(gray_crop.size) if gray_crop.size > 0 else 0
        if contrast >= 0.50:
            glare = max(0.0, (sat_ratio - 0.75) / 0.25) if sat_ratio > 0.75 else 0.0
        else:
            glare = min(1.0, sat_ratio / 0.40)

        uniformity = self.quality_analyzer.compute_illumination_uniformity(gray_crop)

        plate_quality = self.quality_analyzer.compute_overall_quality(
            brightness, contrast, sharpness, glare, uniformity
        )

        # 2. Assess Rule-Based Compliance and Physical Integrity
        anomaly_flags, condition, readability = self._evaluate_anomalies_and_condition(
            gray_crop, crop, aspect_ratio, plate_quality, sharpness, glare, contrast
        )

        return CandidatePlateRegion(
            region_id=region_id,
            bbox=bbox,
            confidence=confidence,
            aspect_ratio=aspect_ratio,
            plate_quality_score=round(plate_quality, 3),
            plate_brightness=round(brightness, 3),
            plate_contrast=round(contrast, 3),
            plate_sharpness=round(sharpness, 3),
            plate_glare=round(glare, 3),
            condition=condition,
            readability=readability,
            anomaly_flags=anomaly_flags,
        )

    def _evaluate_anomalies_and_condition(
        self,
        gray_crop: np.ndarray,
        bgr_crop: np.ndarray,
        aspect_ratio: float,
        quality: float,
        sharpness: float,
        glare: float,
        contrast: float
    ) -> Tuple[PlateAnomalyFlags, str, str]:
        """
        Rule-based heuristic evaluation of plate physical condition and compliance.
        """
        is_broken = False
        is_damaged = False
        is_modified = False
        is_non_standard = False
        is_obscured = False
        is_unreadable = False

        # 1. Geometric Aspect Ratio Compliance (HSRP Standard vs Non-standard)
        # Rectangular HSRP is typically 3.0 to 5.5. Square is 1.3 to 2.2.
        is_standard_geom = (3.0 <= aspect_ratio <= 5.5) or (1.3 <= aspect_ratio <= 2.2)
        if not is_standard_geom:
            is_modified = True
            is_non_standard = True

        # 2. Obscured / Dirty Check (Low contrast + patchy lighting)
        if contrast < 0.40 and quality < 0.55:
            is_obscured = True

        # 3. Readability Classification
        if sharpness < 0.15 or (glare > 0.80 and contrast < 0.35) or quality < 0.30:
            is_unreadable = True
            readability = "CRITICAL"
        elif quality < 0.45:
            readability = "POOR"
        elif quality < 0.65:
            readability = "FAIR"
        elif quality < 0.80:
            readability = "GOOD"
        else:
            readability = "EXCELLENT"

        # 4. Physical Damage / Crack Heuristic
        # Plate has cracks, fractures, or heavy unevenness
        if not is_unreadable and not is_obscured:
            if quality < 0.68 or is_modified:
                is_damaged = True

        # 5. Condition Category Classification
        if is_unreadable:
            condition = "UNREADABLE"
        elif is_damaged:
            condition = "DAMAGED"
        elif is_obscured:
            condition = "OCCLUDED"
        elif is_modified or quality < 0.70:
            condition = "PARTIAL"
        else:
            condition = "NORMAL"

        flags = PlateAnomalyFlags(
            missing_plate=False,
            broken_plate=is_broken,
            damaged_plate=is_damaged,
            modified_plate=is_modified,
            non_standard_plate=is_non_standard,
            obscured_plate=is_obscured,
            unreadable_plate=is_unreadable,
        )

        return flags, condition, readability
