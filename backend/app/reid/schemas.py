from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class VehicleVisualSignature(BaseModel):
    """Normalized visual vehicle feature signature."""
    vehicle_color: str = Field("unknown", description="white | black | silver | grey | red | blue | green | yellow | orange | brown | other | unknown")
    color_confidence: float = Field(0.85, ge=0.0, le=1.0)
    vehicle_type: str = Field("unknown", description="sedan | hatchback | SUV | pickup | van | bus | truck | motorcycle | unknown")
    type_confidence: float = Field(0.85, ge=0.0, le=1.0)
    make: Optional[str] = Field("unknown", description="Manufacturer if known e.g. Hyundai, Tata, Maruti")
    model: Optional[str] = Field("unknown", description="Model if known e.g. Creta, Swift, City")
    aspect_ratio: float = Field(1.5, description="Bounding box aspect ratio width/height")
    appearance_descriptor: Optional[List[float]] = Field(None, description="Compact normalized visual feature descriptor")
    distinctive_features: List[str] = Field(default_factory=list, description="Visual markers e.g. roof_rails, window_tint_dark, sticker_qr")
    plate_number: Optional[str] = Field(None, description="Plate number if readable")
    ocr_confidence: Optional[float] = Field(None, description="OCR confidence if plate detected")


class FeatureSimilarityBreakdown(BaseModel):
    """Fine-grained breakdown of individual feature similarity scores."""
    color_similarity: float = Field(..., ge=0.0, le=1.0)
    type_similarity: float = Field(..., ge=0.0, le=1.0)
    appearance_similarity: float = Field(..., ge=0.0, le=1.0)
    shape_similarity: float = Field(..., ge=0.0, le=1.0)
    plate_similarity: Optional[float] = Field(None, ge=0.0, le=1.0)
    distinctive_features_similarity: float = Field(1.0, ge=0.0, le=1.0)
    weights_applied: Dict[str, float] = Field(..., description="Normalized feature weights summing to 1.0")


class ReIDMatchResult(BaseModel):
    """Result of vehicle re-identification matching between two sightings."""
    is_match: bool
    classification: str = Field(..., description="HIGH_CONFIDENCE_MATCH | POSSIBLE_MATCH | LOW_CONFIDENCE | NO_MATCH")
    overall_score: float = Field(..., ge=0.0, le=1.0)
    evidence: FeatureSimilarityBreakdown
    delta_time_seconds: Optional[float] = None
    distance_meters: Optional[float] = None
    speed_kmh: Optional[float] = None
    is_temporally_plausible: bool = True
    method_used: str = Field(..., description="PLATE_AND_VISUAL_REID | VISUAL_REID_FALLBACK | PLATE_EXACT_MATCH")
    explanation: str
    reid_latency_ms: float

    model_config = ConfigDict(from_attributes=True)


class ReIDObservationPayload(BaseModel):
    """Observation data payload for matching."""
    observation_id: Optional[str] = None
    camera_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    signature: VehicleVisualSignature
    lat: Optional[float] = None
    lon: Optional[float] = None


class ReIDMatchRequest(BaseModel):
    """Request to match two observations."""
    source: ReIDObservationPayload
    target: ReIDObservationPayload
    persist_match: bool = False


class ReIDTrackCandidate(BaseModel):
    """Ranked candidate observation matching a source vehicle."""
    candidate_id: str
    detection_id: Optional[int] = None
    camera_id: str
    camera_name: Optional[str] = None
    timestamp: datetime
    plate_number: Optional[str] = None
    plate_readable: bool
    vehicle_color: str
    vehicle_type: str
    match_result: ReIDMatchResult


class ReIDTrackResponse(BaseModel):
    """Response containing ranked candidate vehicle sightings."""
    source_observation_id: str
    source_camera_id: str
    source_plate: Optional[str] = None
    source_color: str
    source_type: str
    total_candidates_evaluated: int
    ranked_candidates: List[ReIDTrackCandidate]
    execution_latency_ms: float


class ReIDDemoStep(BaseModel):
    """Individual step in a multi-camera tracking scenario."""
    step_number: int
    camera_id: str
    camera_name: str
    timestamp: str
    plate_display: str
    plate_status: str  # READABLE | OCCLUDED | UNREADABLE
    ocr_confidence: Optional[float]
    vehicle_color: str
    vehicle_type: str
    match_score: float
    match_classification: str
    reid_method: str
    evidence_summary: List[str]


class ReIDDemoScenarioResponse(BaseModel):
    """Complete multi-camera vehicle tracking demonstration scenario."""
    scenario_id: str
    title: str
    description: str
    tracked_vehicle_id: str
    ground_truth_plate: str
    steps: List[ReIDDemoStep]
    distractor_vehicles: List[Dict[str, Any]]
    summary: str
