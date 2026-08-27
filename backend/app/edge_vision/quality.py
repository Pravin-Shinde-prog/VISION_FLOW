import cv2
import numpy as np
from app.edge_vision.schemas import ImageQualityMetrics


class ImageQualityAnalyzer:
    """
    Evaluates measurable heuristic image quality metrics for vehicle & plate imagery.
    All scores are normalized to standard [0.0, 1.0] scale.
    """

    def analyze(self, bgr_image: np.ndarray) -> ImageQualityMetrics:
        if len(bgr_image.shape) == 3:
            gray = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = bgr_image

        brightness = self.compute_brightness_score(gray)
        contrast = self.compute_contrast_score(gray)
        sharpness = self.compute_sharpness_score(gray)
        glare = self.compute_glare_score(gray)
        uniformity = self.compute_illumination_uniformity(gray)
        overall = self.compute_overall_quality(brightness, contrast, sharpness, glare, uniformity)

        return ImageQualityMetrics(
            brightness_score=round(brightness, 3),
            contrast_score=round(contrast, 3),
            sharpness_score=round(sharpness, 3),
            glare_score=round(glare, 3),
            illumination_uniformity=round(uniformity, 3),
            overall_quality_score=round(overall, 3)
        )

    def compute_brightness_score(self, gray: np.ndarray) -> float:
        """
        Optimal average luminance for ANPR is typically around 110-150.
        Scores near 1.0 denote balanced lighting; near 0.0 denote severe underexposure or washout.
        """
        mean_lum = float(np.mean(gray))
        # Ideal range [110, 150]
        if 110 <= mean_lum <= 150:
            return 1.0
        elif mean_lum < 110:
            return max(0.0, mean_lum / 110.0)
        else:
            return max(0.0, 1.0 - ((mean_lum - 150.0) / 105.0))

    def compute_contrast_score(self, gray: np.ndarray) -> float:
        """
        Evaluates standard deviation and dynamic range of luminance.
        High contrast (>50 std dev) scores near 1.0.
        """
        std_lum = float(np.std(gray))
        # Standard deviation > 55 gives score 1.0
        return min(1.0, std_lum / 55.0)

    def compute_sharpness_score(self, gray: np.ndarray) -> float:
        """
        Calculates Laplacian variance sigma^2(Laplacian(I)) to estimate high-frequency focus.
        Laplacian variance > 250 is considered sharp.
        """
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = float(laplacian.var())
        # Sigmoid or logarithmic normalization for variance
        score = min(1.0, np.log1p(variance) / np.log1p(350.0))
        return max(0.0, float(score))

    def compute_glare_score(self, gray: np.ndarray) -> float:
        """
        Measures proportion of saturated specular pixels (intensity > 245).
        """
        saturated_pixels = np.count_nonzero(gray >= 245)
        total_pixels = gray.size
        ratio = saturated_pixels / float(total_pixels)
        # Ratio of 10% saturated pixels gives max glare score of 1.0
        return min(1.0, ratio / 0.10)

    def compute_illumination_uniformity(self, gray: np.ndarray) -> float:
        """
        Divides the image into a 4x4 grid and measures variation in average regional luminance.
        Uniform lighting across tiles gives high score.
        """
        h, w = gray.shape[:2]
        tile_h, tile_w = max(1, h // 4), max(1, w // 4)
        means = []
        for i in range(4):
            for j in range(4):
                tile = gray[i * tile_h:(i + 1) * tile_h, j * tile_w:(j + 1) * tile_w]
                if tile.size > 0:
                    means.append(np.mean(tile))

        if not means:
            return 1.0

        grid_std = float(np.std(means))
        # Lower grid std means higher uniformity
        return max(0.0, 1.0 - (grid_std / 70.0))

    def compute_overall_quality(
        self,
        brightness: float,
        contrast: float,
        sharpness: float,
        glare: float,
        uniformity: float
    ) -> float:
        """
        Composite weighted score prioritizing contrast and sharpness for OCR readiness.
        """
        score = (
            0.30 * contrast +
            0.30 * sharpness +
            0.20 * brightness +
            0.10 * uniformity +
            0.10 * (1.0 - glare)
        )
        return max(0.0, min(1.0, score))
