import cv2
import numpy as np
from typing import Tuple
from app.edge_vision.schemas import PreprocessingConfig


class ImagePreprocessor:
    """
    Applies configurable image enhancement operations tailored for ANPR license plate visibility:
    - Luminance normalization & adaptive histogram equalization (CLAHE)
    - Specular glare suppression & shadow dynamic-range compensation
    - Bilateral edge-preserving noise reduction
    - Unsharp mask sharpening for character stroke contrast
    """

    def __init__(self, config: PreprocessingConfig = None):
        self.config = config or PreprocessingConfig()

    def resize_if_needed(self, image: np.ndarray) -> Tuple[np.ndarray, float]:
        """Resizes large images to target_max_dimension to preserve low edge latency."""
        h, w = image.shape[:2]
        max_dim = self.config.target_max_dimension
        if max(h, w) <= max_dim:
            return image, 1.0

        scale = max_dim / float(max(h, w))
        new_w = int(w * scale)
        new_h = int(h * scale)
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        return resized, scale

    def enhance_frame(self, bgr_image: np.ndarray) -> np.ndarray:
        """
        Runs the full configurable enhancement pipeline on a BGR image frame.
        """
        enhanced = bgr_image.copy()

        # 1. Convert to LAB color space for luminance manipulation without distorting hues
        lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)

        # 2. Shadow & Glare Compensation (Gamma Correction + Histogram Stretching)
        if self.config.enable_glare_reduction:
            l_channel = self._compensate_illumination(l_channel)

        # 3. Contrast Limited Adaptive Histogram Equalization (CLAHE)
        if self.config.enable_clahe:
            clahe = cv2.createCLAHE(
                clipLimit=self.config.clahe_clip_limit,
                tileGridSize=(8, 8)
            )
            l_channel = clahe.apply(l_channel)

        # 4. Bilateral Edge-Preserving Denoising on Luminance
        if self.config.enable_denoising:
            l_channel = cv2.bilateralFilter(l_channel, d=5, sigmaColor=35, sigmaSpace=35)

        # 5. Unsharp Mask Sharpening for Character Strokes
        if self.config.enable_sharpening and self.config.sharpen_strength > 0:
            gaussian = cv2.GaussianBlur(l_channel, (0, 0), sigmaX=2.0)
            unsharp = cv2.addWeighted(
                l_channel, 1.0 + self.config.sharpen_strength,
                gaussian, -self.config.sharpen_strength,
                0
            )
            l_channel = np.clip(unsharp, 0, 255).astype(np.uint8)

        # Recombine LAB channels and convert back to BGR
        merged_lab = cv2.merge([l_channel, a_channel, b_channel])
        enhanced_bgr = cv2.cvtColor(merged_lab, cv2.COLOR_LAB2BGR)
        return enhanced_bgr

    def _compensate_illumination(self, l_channel: np.ndarray) -> np.ndarray:
        """
        Compresses specular glare highlights and lifts harsh shadow regions.
        """
        mean_lum = np.mean(l_channel)
        # Adaptively compute gamma based on overall image brightness
        if mean_lum < 90:
            gamma = 0.80  # Lift underexposed shadows
        elif mean_lum > 170:
            gamma = 1.25  # Tame severe overexposure / daytime glare
        else:
            gamma = 1.0

        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype(np.uint8)
        return cv2.LUT(l_channel, table)

    def extract_edge_representation(self, gray_image: np.ndarray) -> np.ndarray:
        """
        Produces a high-contrast vertical edge representation (Sobel X + Morphological BlackHat)
        designed to emphasize license plate vertical character strokes.
        """
        # Morphological Top-Hat and Black-Hat to isolate local contrast
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 5))
        blackhat = cv2.morphologyEx(gray_image, cv2.MORPH_BLACKHAT, rect_kernel)
        tophat = cv2.morphologyEx(gray_image, cv2.MORPH_TOPHAT, rect_kernel)
        contrast_boosted = cv2.add(cv2.subtract(gray_image, blackhat), tophat)

        # Sobel Vertical Gradient (dx=1, dy=0)
        sobel_x = cv2.Sobel(contrast_boosted, cv2.CV_32F, 1, 0, ksize=3)
        sobel_x = np.absolute(sobel_x)
        min_val, max_val = np.min(sobel_x), np.max(sobel_x)
        if max_val > min_val:
            sobel_norm = ((sobel_x - min_val) / (max_val - min_val) * 255).astype(np.uint8)
        else:
            sobel_norm = np.zeros_like(gray_image)

        # Gaussian smoothing to connect adjacent vertical strokes
        blurred = cv2.GaussianBlur(sobel_norm, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        return thresh
