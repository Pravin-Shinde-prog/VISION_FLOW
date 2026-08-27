import cv2
import numpy as np
from typing import List, Optional
from app.reid.schemas import VehicleVisualSignature
from app.reid.color_extractor import VehicleColorExtractor


class VisualFeatureExtractor:
    """
    Extracts explainable, lightweight visual appearance descriptors:
    - 3x3 Spatial Grid Color Histograms (HSV)
    - Horizontal and Vertical Edge Density Profiles (Sobel gradients)
    - Geometry & Aspect Ratio
    """

    @classmethod
    def extract_descriptor(cls, vehicle_bgr: np.ndarray) -> List[float]:
        if vehicle_bgr is None or vehicle_bgr.size == 0:
            # Return zero descriptor
            return [0.0] * 32

        # Standardize size for consistent spatial descriptor
        resized = cv2.resize(vehicle_bgr, (128, 96), interpolation=cv2.INTER_AREA)
        hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

        features: List[float] = []

        # 1. 3x3 Spatial Grid Color Means & Standard Deviations (H, S, V) -> 18 features
        grid_h, grid_w = 32, 42
        for r in range(3):
            for c in range(3):
                cell_hsv = hsv[r*grid_h:(r+1)*grid_h, c*grid_w:(c+1)*grid_w]
                h_mean = float(np.mean(cell_hsv[:, :, 0]) / 180.0)
                s_mean = float(np.mean(cell_hsv[:, :, 1]) / 255.0)
                features.extend([round(h_mean, 4), round(s_mean, 4)])

        # 2. Vertical & Horizontal Edge Density Profiles (Sobel gradients) -> 8 features
        sobel_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        mag = cv2.magnitude(sobel_x, sobel_y)

        # 4 quadrant edge intensities
        q_h, q_w = 48, 64
        for r in range(2):
            for c in range(2):
                cell_mag = mag[r*q_h:(r+1)*q_h, c*q_w:(c+1)*q_w]
                edge_val = float(np.mean(cell_mag) / 255.0)
                features.append(round(min(1.0, edge_val), 4))

        # 3. Luminance percentiles -> 6 features
        p10 = float(np.percentile(gray, 10) / 255.0)
        p30 = float(np.percentile(gray, 30) / 255.0)
        p50 = float(np.percentile(gray, 50) / 255.0)
        p70 = float(np.percentile(gray, 70) / 255.0)
        p90 = float(np.percentile(gray, 90) / 255.0)
        contrast = float(np.std(gray) / 128.0)
        features.extend([round(p10, 4), round(p30, 4), round(p50, 4), round(p70, 4), round(p90, 4), round(min(1.0, contrast), 4)])

        return features[:32]

    @classmethod
    def create_signature(
        cls,
        vehicle_bgr: Optional[np.ndarray] = None,
        color_hint: Optional[str] = None,
        type_hint: Optional[str] = None,
        plate_number: Optional[str] = None,
        ocr_conf: Optional[float] = None,
        distinctive_features: Optional[List[str]] = None
    ) -> VehicleVisualSignature:
        if vehicle_bgr is not None and vehicle_bgr.size > 0:
            h, w = vehicle_bgr.shape[:2]
            aspect = round(w / float(h), 2)
            detected_color, color_conf = VehicleColorExtractor.estimate_from_crop(vehicle_bgr)
            color = color_hint or detected_color
            descriptor = cls.extract_descriptor(vehicle_bgr)
        else:
            aspect = 1.5
            color = color_hint or "unknown"
            color_conf = 0.85
            descriptor = None

        return VehicleVisualSignature(
            vehicle_color=color,
            color_confidence=color_conf,
            vehicle_type=type_hint or "unknown",
            type_confidence=0.85 if type_hint else 0.50,
            make="unknown",
            model="unknown",
            aspect_ratio=aspect,
            appearance_descriptor=descriptor,
            distinctive_features=distinctive_features or [],
            plate_number=plate_number,
            ocr_confidence=ocr_conf,
        )
