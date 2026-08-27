from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.edge_vision.schemas import ImageQualityMetrics, PlateAnomalyFlags, CandidatePlateRegion


class PlateComponents(BaseModel):
    """Structured decomposition of an Indian license plate."""
    state_code: Optional[str] = Field(None, description="2-letter Indian State / UT code (e.g. MH, DL, KA)")
    district_code: Optional[str] = Field(None, description="2-digit RTO district code (e.g. 12 for Pune, 01 for Mumbai)")
    series: Optional[str] = Field(None, description="1 to 3 letter registration series (e.g. AB, C, ZZ)")
    registration_number: Optional[str] = Field(None, description="4-digit vehicle serial number (e.g. 1234)")


class PlateValidationResult(BaseModel):
    """Result of Indian license plate format validation."""
    is_valid: bool
    format_type: str = Field("standard_hsrp", description="standard_hsrp | bharat_series | vintage_commercial | invalid")
    components: Optional[PlateComponents] = None
    validation_message: str
    confidence_penalty: float = 0.0


class PlateNormalizationResult(BaseModel):
    """Result of positional character confusion normalization."""
    raw_text: str
    normalized_plate: Optional[str]
    substitutions_made: List[str]
    is_normalized: bool


class PlateOCRResult(BaseModel):
    """Normalized OCR reading and validation metadata."""
    raw_text: str
    normalized_plate: Optional[str]
    ocr_confidence: float = Field(..., ge=0.0, le=1.0)
    format_valid: bool
    final_confidence: float = Field(..., ge=0.0, le=1.0)
    readability: str = Field(..., description="READABLE | LOW_CONFIDENCE | UNREADABLE")
    components: Optional[PlateComponents] = None
    ocr_engine: str = "ONNX-PP-OCRv4"
    engine_version: str = "anpr_v1.0"
    ocr_latency_ms: float


class ANPRCandidateResult(BaseModel):
    """Candidate plate bounding box enriched with OCR reading and ranking score."""
    region_id: int
    bbox: List[int]
    confidence: float
    aspect_ratio: float
    plate_quality_score: float
    condition: str
    anomaly_flags: PlateAnomalyFlags
    ocr_result: PlateOCRResult
    rank_score: float
    cropped_plate_b64: Optional[str] = None


class ANPRProcessResponse(BaseModel):
    """Complete end-to-end ANPR metadata response."""
    data_source: str = "anpr_engine"
    pipeline_version: str = "anpr_v1.0"
    processed_at: datetime
    camera_id: Optional[str] = None
    frame_width: int
    frame_height: int
    total_latency_ms: float
    edge_vision_latency_ms: float
    ocr_latency_ms: float
    plate_detected: bool
    primary_plate: Optional[ANPRCandidateResult] = None
    all_candidates: List[ANPRCandidateResult] = []
    image_quality: ImageQualityMetrics
    summary_condition: str
    annotated_frame_b64: Optional[str] = None
    cropped_plate_b64: Optional[str] = None
    persisted_detection_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ANPRBenchmarkResponse(BaseModel):
    """Results from the automated test scenario benchmark."""
    total_samples: int
    exact_matches: int
    exact_match_rate: float
    normalized_matches: int
    normalized_match_rate: float
    format_valid_count: int
    format_valid_rate: float
    average_latency_ms: float
    results_breakdown: List[Dict[str, Any]]
    disclaimer: str = "Prototype benchmark on controlled test scenarios — not representative of real-world multi-lane field accuracy."
