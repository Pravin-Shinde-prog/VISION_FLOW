import cv2
import numpy as np
from typing import Tuple, Dict

# Supported Color Categories in VISION_FLOW
VALID_COLORS = [
    "white",
    "black",
    "silver",
    "grey",
    "red",
    "blue",
    "green",
    "yellow",
    "orange",
    "brown",
    "other",
    "unknown",
]

# Color Compatibility Matrix (Perceptual similarity between colors)
COLOR_COMPATIBILITY: Dict[Tuple[str, str], float] = {
    # Exact matches
    ("white", "white"): 1.0,
    ("black", "black"): 1.0,
    ("silver", "silver"): 1.0,
    ("grey", "grey"): 1.0,
    ("red", "red"): 1.0,
    ("blue", "blue"): 1.0,
    ("green", "green"): 1.0,
    ("yellow", "yellow"): 1.0,
    ("orange", "orange"): 1.0,
    ("brown", "brown"): 1.0,

    # Perceptually close neutral / metallic colors
    ("white", "silver"): 0.70,
    ("silver", "white"): 0.70,
    ("silver", "grey"): 0.80,
    ("grey", "silver"): 0.80,
    ("grey", "black"): 0.55,
    ("black", "grey"): 0.55,

    # Warm tones
    ("red", "orange"): 0.65,
    ("orange", "red"): 0.65,
    ("orange", "yellow"): 0.65,
    ("yellow", "orange"): 0.65,
    ("brown", "orange"): 0.50,
    ("orange", "brown"): 0.50,
    ("brown", "black"): 0.50,
    ("black", "brown"): 0.50,

    # Cool tones
    ("blue", "black"): 0.40,
    ("black", "blue"): 0.40,
    ("green", "blue"): 0.35,
    ("blue", "green"): 0.35,
}


class VehicleColorExtractor:
    """
    Extracts dominant vehicle color from localized vehicle body crops.
    Excludes road background (bottom 25%) and windshield/sky reflection (top 20%).
    """

    @classmethod
    def compute_similarity(cls, color1: str, color2: str) -> float:
        c1 = color1.strip().lower() if color1 else "unknown"
        c2 = color2.strip().lower() if color2 else "unknown"

        if c1 == "unknown" or c2 == "unknown":
            return 0.50  # Neutral prior when one color is unobserved

        if c1 == c2:
            return 1.0

        pair = (c1, c2)
        if pair in COLOR_COMPATIBILITY:
            return COLOR_COMPATIBILITY[pair]

        # Distinct color mismatch
        return 0.05

    @classmethod
    def estimate_from_crop(cls, vehicle_bgr: np.ndarray) -> Tuple[str, float]:
        """
        Determines dominant body color from BGR vehicle crop.
        """
        if vehicle_bgr is None or vehicle_bgr.size == 0:
            return "unknown", 0.0

        h, w = vehicle_bgr.shape[:2]
        # Crop central body region: Y from 25% to 75%, X from 15% to 85%
        body_crop = vehicle_bgr[int(h * 0.25):int(h * 0.75), int(w * 0.15):int(w * 0.85)]
        if body_crop.size == 0:
            body_crop = vehicle_bgr

        # Convert to HSV
        hsv = cv2.cvtColor(body_crop, cv2.COLOR_BGR2HSV)
        h_channel, s_channel, v_channel = cv2.split(hsv)

        mean_v = np.mean(v_channel)
        mean_s = np.mean(s_channel)
        mean_h = np.mean(h_channel)

        # 1. Neutral / Achromatic Classifications
        if mean_s < 35:
            if mean_v > 190:
                return "white", 0.92
            elif mean_v < 60:
                return "black", 0.90
            elif mean_v > 130:
                return "silver", 0.85
            else:
                return "grey", 0.85

        # 2. Chromatic Classifications (Hue 0 - 180 in OpenCV)
        if (mean_h < 10 or mean_h > 165) and mean_s > 40:
            return "red", 0.88
        elif 10 <= mean_h < 25:
            return "orange", 0.84
        elif 25 <= mean_h < 35:
            return "yellow", 0.84
        elif 35 <= mean_h < 85:
            return "green", 0.86
        elif 85 <= mean_h < 135:
            return "blue", 0.90
        elif 135 <= mean_h <= 165:
            return "brown" if mean_v < 100 else "red", 0.80

        return "other", 0.60
