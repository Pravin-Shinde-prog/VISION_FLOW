from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class PlateSighting(BaseModel):
    """Normalized plate sighting observation from camera ANPR."""
    plate_number: str = Field(..., description="Raw or formatted license plate")
    camera_id: str = Field(..., description="Alphanumeric camera ID (e.g. CAM_PUN_001)")
    timestamp: datetime
    detection_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    ocr_confidence: float = Field(0.95, ge=0.0, le=1.0)
    vehicle_color: Optional[str] = Field("unknown")
    vehicle_type: Optional[str] = Field("unknown")
    aspect_ratio: Optional[float] = Field(1.5)
    snapshot_path: Optional[str] = Field(None)


class EvidenceItem(BaseModel):
    """Individual item in the structured forensic evidence checklist."""
    category: str = Field(..., description="PLATE_EVIDENCE | TEMPORAL_EVIDENCE | SPATIAL_EVIDENCE | KINEMATIC_EVIDENCE | VEHICLE_REID_EVIDENCE")
    verdict: str = Field(..., description="CONSISTENT | CONTRADICTORY | INCONCLUSIVE | NORMAL")
    description: str
    severity_impact: float = Field(0.0, ge=0.0, le=1.0)


class GhostPlateAlertRecord(BaseModel):
    """Complete forensic ghost plate anomaly record."""
    alert_id: str
    plate_number: str
    normalized_plate: str
    alert_type: str = Field(..., description="POSSIBLE_CLONED_PLATE | TOPOLOGY_INCONSISTENT | NORMAL_REPEAT_SIGHTING | NO_ANOMALY")
    severity: str = Field(..., description="CRITICAL | HIGH | MEDIUM | LOW | NONE")
    status: str = Field("NEW", description="NEW | REVIEWED | DISMISSED | CONFIRMED_BY_OPERATOR")
    source_camera_id: str
    target_camera_id: str
    source_timestamp: datetime
    target_timestamp: datetime
    observed_delta_seconds: float
    minimum_feasible_time_seconds: float
    distance_meters: float
    required_speed_kmh: float
    speed_limit_kmh: float
    graph_status: str
    anomaly_score: float = Field(..., ge=0.0, le=1.0)
    ocr_confidence_product: float
    reid_similarity_score: Optional[float] = None
    evidence_checklist: List[EvidenceItem]
    explanation: str
    source_snapshot_ref: str
    target_snapshot_ref: str
    is_simulated: bool = True
    created_at: datetime
    analysis_latency_ms: float

    model_config = ConfigDict(from_attributes=True)


class GhostPlateAnalysisRequest(BaseModel):
    """Request to analyze pairwise transition between two plate sightings."""
    source_sighting: PlateSighting
    target_sighting: PlateSighting
    congestion_tolerance_factor: float = Field(3.5, ge=1.0, le=10.0)


class LiveSightingEvaluationRequest(BaseModel):
    """Request to evaluate a live plate sighting against recent sighting history."""
    sighting: PlateSighting
    history_window_minutes: int = Field(120, ge=5, le=1440)


class LiveSightingEvaluationResponse(BaseModel):
    """Response containing any detected anomaly alerts for the new sighting."""
    evaluated_sighting: PlateSighting
    previous_sightings_found: int
    alerts_generated: List[GhostPlateAlertRecord]
    is_suspicious: bool
    highest_anomaly_score: float
    execution_latency_ms: float


class GhostPlateStatusUpdate(BaseModel):
    """Request to update an alert review status."""
    status: str = Field(..., description="NEW | REVIEWED | DISMISSED | CONFIRMED_BY_OPERATOR")
    notes: Optional[str] = None


class GhostPlateScenario(BaseModel):
    """Pre-built test scenario for demonstrating ghost plate detection capabilities."""
    scenario_id: str
    title: str
    description: str
    expected_classification: str
    expected_severity: str
    alert: GhostPlateAlertRecord
