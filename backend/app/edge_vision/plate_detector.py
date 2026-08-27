import cv2
import numpy as np
from typing import List, Dict, Any


class PlateRegionDetector:
    """
    Classical computer vision foundation for localizing candidate license plate regions.
    Uses Morphological TopHat/BlackHat, Sobel vertical gradients, and Indian plate aspect-ratio contour filters.
    Provides candidate bounding boxes, crop matrices, and confidence heuristics.
    """

    def __init__(
        self,
        min_aspect_ratio: float = 1.2,
        max_aspect_ratio: float = 6.5,
        min_area_ratio: float = 0.001,
        max_area_ratio: float = 0.25
    ):
        self.min_aspect_ratio = min_aspect_ratio
        self.max_aspect_ratio = max_aspect_ratio
        self.min_area_ratio = min_area_ratio
        self.max_area_ratio = max_area_ratio

    def detect_candidate_regions(self, bgr_image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Locates candidate plate regions in the input image.
        Returns a list of dicts with: bbox [x1, y1, x2, y2], confidence, aspect_ratio, cropped_bgr.
        """
        h, w = bgr_image.shape[:2]
        total_area = float(h * w)

        gray = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)

        # 1. Morphological BlackHat / TopHat to highlight text within plate boundary
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 5))
        blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, rect_kernel)
        tophat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, rect_kernel)
        contrast = cv2.add(cv2.subtract(gray, blackhat), tophat)

        # 2. Vertical Gradient to locate dense character edges
        sobel_x = cv2.Sobel(contrast, cv2.CV_32F, 1, 0, ksize=3)
        sobel_x = np.absolute(sobel_x)
        min_v, max_v = np.min(sobel_x), np.max(sobel_x)
        if max_v > min_v:
            grad_norm = ((sobel_x - min_v) / (max_v - min_v) * 255).astype(np.uint8)
        else:
            grad_norm = np.zeros_like(gray)

        # 3. Smooth and Threshold
        blurred = cv2.GaussianBlur(grad_norm, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # 4. Morphological Close with wide horizontal kernel to connect license plate characters
        close_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 5))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, close_kernel)

        # 5. Find Contours
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        candidates: List[Dict[str, Any]] = []

        for cnt in contours:
            x, y, cw, ch = cv2.boundingRect(cnt)
            area = cw * ch
            area_ratio = area / total_area

            # Area Filter
            if not (self.min_area_ratio <= area_ratio <= self.max_area_ratio):
                continue

            aspect_ratio = float(cw) / float(ch) if ch > 0 else 0

            # Aspect Ratio Filter (Standard Indian rectangular plates ~3.0 to 5.5, square ~1.2 to 2.2)
            if not (self.min_aspect_ratio <= aspect_ratio <= self.max_aspect_ratio):
                continue

            # Extent (Rectangular fill factor - realistic for text contours is > 0.20)
            contour_area = cv2.contourArea(cnt)
            extent = contour_area / float(area) if area > 0 else 0
            if extent < 0.20:
                continue

            # Crop Region with slight margin
            pad_x = int(cw * 0.04)
            pad_y = int(ch * 0.06)
            x1 = max(0, x - pad_x)
            y1 = max(0, y - pad_y)
            x2 = min(w, x + cw + pad_x)
            y2 = min(h, y + ch + pad_y)

            crop = bgr_image[y1:y2, x1:x2]
            if crop.size == 0 or crop.shape[0] < 8 or crop.shape[1] < 20:
                continue

            # Geometric Confidence Scoring
            # Standard rectangular plate aspect ratio peak ~3.8 to 4.5
            ratio_fit = 1.0 - min(1.0, abs(aspect_ratio - 4.0) / 3.0)
            extent_fit = min(1.0, extent / 0.50)
            confidence = round(0.6 * ratio_fit + 0.4 * extent_fit, 3)

            candidates.append({
                "bbox": [x1, y1, x2, y2],
                "confidence": max(0.40, confidence),
                "aspect_ratio": round(aspect_ratio, 2),
                "cropped_bgr": crop,
                "contour": cnt,
            })

        # Sort candidate regions by confidence descending
        candidates.sort(key=lambda c: c["confidence"], reverse=True)
        return candidates[:3]
