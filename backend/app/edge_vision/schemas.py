from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ImageQualityMetrics(BaseModel):
    """
    Engineered heuristic quality metrics evaluated on the input frame.
    All scores are normalized to [0.0, 1.0].
    """
    brightness_score: float = Field(..., description="Overall luminance balance (0.0: dark, 1.0: optimal, >1.0/low: skewed)")
    contrast_score: float = Field(..., description="Dynamic range & luminance variance (0.0: flat/gray, 1.0: high dynamic range)")
    sharpness_score: float = Field(..., description="Edge gradient sharpness / focus (0.0: blurry, 1.0: sharp)")
    glare_score: float = Field(..., description="Proportion of overexposed/specular reflection pixels (0.0: no glare, 1.0: severe glare)")
    illumination_uniformity: float = Field(..., description="Uniformity of light across frame grid (0.0: heavy shadows, 1.0: even)")
    overall_quality_score: float = Field(..., description="Weighted composite quality index (0.0 - 1.0)")


class PlateAnomalyFlags(BaseModel):
    """
    Rule-based license plate compliance and physical integrity anomaly flags.
    Explicitly focused on license plate physical state.
    """
    missing_plate: bool = Field(default=False, description="No viable license plate candidate located in frame")
    broken_plate: bool = Field(default=False, description="Plate contour exhibits structural breakage or fragmented border")
    damaged_plate: bool = Field(default=False, description="Plate surface has localized physical defects, cracks, or dents")
    modified_plate: bool = Field(default=False, description="Plate dimensions or aspect ratio deviate from standard HSRP geometry")
    non_standard_plate: bool = Field(default=False, description="Plate background or font style deviates from standard RTO formats")
    obscured_plate: bool = Field(default=False, description="Plate is partially obscured by dirt, frame brackets, or mud")
    unreadable_plate: bool = Field(default=False, description="Plate quality is too degraded for reliable character recognition")


class CandidatePlateRegion(BaseModel):
    """
    Bounding box and quality metrics for a localized candidate license plate region.
    """
    region_id: int
    bbox: List[int] = Field(..., description="[x1, y1, x2, y2] bounding box coordinates in original frame")
    confidence: float = Field(..., description="Geometric & gradient confidence score of plate candidate (0.0 - 1.0)")
    aspect_ratio: float = Field(..., description="Width-to-height ratio of candidate region")
    plate_quality_score: float = Field(..., description="Localized quality score of plate crop (0.0 - 1.0)")
    plate_brightness: float
    plate_contrast: float
    plate_sharpness: float
    plate_glare: float
    condition: str = Field(..., description="NORMAL | PARTIAL | OCCLUDED | DAMAGED | UNREADABLE")
    readability: str = Field(..., description="EXCELLENT | GOOD | FAIR | POOR | CRITICAL")
    anomaly_flags: PlateAnomalyFlags
    cropped_plate_b64: Optional[str] = Field(default=None, description="Base64-encoded JPEG crop of candidate plate")


class PreprocessingConfig(BaseModel):
    """
    Configurable parameters for the edge image enhancement pipeline.
    """
    enable_clahe: bool = Field(default=True, description="Apply Contrast Limited Adaptive Histogram Equalization")
    clahe_clip_limit: float = Field(default=2.5, ge=1.0, le=10.0)
    enable_denoising: bool = Field(default=True, description="Apply bilateral edge-preserving smoothing")
    enable_sharpening: bool = Field(default=True, description="Apply unsharp masking for stroke enhancement")
    sharpen_strength: float = Field(default=0.5, ge=0.0, le=2.0)
    enable_glare_reduction: bool = Field(default=True, description="Apply highlight compression / shadow normalization")
    target_max_dimension: int = Field(default=1280, ge=320, le=3840)


class EdgeVisionProcessResponse(BaseModel):
    """
    Normalized edge vision metadata returned after frame enhancement and plate analysis.
    """
    data_source: str = "edge_vision"
    pipeline_version: str = "edge_v1.0"
    processed_at: datetime
    camera_id: Optional[str] = None
    frame_width: int
    frame_height: int
    processing_latency_ms: float
    image_quality: ImageQualityMetrics
    plate_detected: bool
    candidate_plates_count: int
    candidate_plates: List[CandidatePlateRegion]
    primary_plate: Optional[CandidatePlateRegion] = None
    overall_anomaly_detected: bool
    summary_condition: str
    enhanced_frame_b64: Optional[str] = Field(default=None, description="Base64-encoded enhanced preview with annotations")
    edge_representation_b64: Optional[str] = Field(default=None, description="Base64-encoded vertical gradient edge map")

    model_config = ConfigDict(from_attributes=True)


class SampleFrameInfo(BaseModel):
    sample_id: str
    title: str
    description: str
    category: str
    filename: str
