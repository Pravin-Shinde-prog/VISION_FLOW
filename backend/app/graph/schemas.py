from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class GraphNode(BaseModel):
    """Camera node in the spatio-temporal directed road network."""
    camera_id: str = Field(..., description="Alphanumeric camera ID (e.g. CAM_PUN_001)")
    name: str
    latitude: float
    longitude: float
    sector: str
    road_name: Optional[str] = None
    is_active: bool = True


class GraphEdge(BaseModel):
    """Directed connection from source camera to destination camera."""
    edge_id: int
    source_camera_id: str
    destination_camera_id: str
    distance_meters: float
    speed_limit_kmh: float
    expected_min_travel_seconds: float
    expected_max_travel_seconds: float
    road_name: Optional[str] = None
    direction: Optional[str] = None


class GraphTopologyResponse(BaseModel):
    """Complete graph topology for GIS visualization."""
    total_nodes: int
    total_edges: int
    nodes: List[GraphNode]
    edges: List[GraphEdge]


class GraphPathResponse(BaseModel):
    """Result of directed shortest path search between two cameras."""
    path_exists: bool
    source_camera_id: str
    target_camera_id: str
    camera_path: List[str]
    node_names_path: List[str]
    edge_ids: List[int]
    total_distance_meters: float
    estimated_min_time_seconds: float
    estimated_max_time_seconds: float
    effective_speed_limit_kmh: float
    hop_count: int
    explanation: str


class TransitionValidationRequest(BaseModel):
    """Request to validate physical/temporal transition between two camera observations."""
    source_camera_id: str
    target_camera_id: str
    source_timestamp: datetime
    target_timestamp: datetime
    vehicle_id: Optional[str] = None
    plate_number: Optional[str] = None
    reid_confidence: Optional[float] = None
    congestion_tolerance_factor: float = Field(3.5, ge=1.0, le=10.0, description="Multiplier for max reasonable travel time")


class TransitionValidationResponse(BaseModel):
    """Result of spatio-temporal transition validation between two sightings."""
    status: str = Field(..., description="TEMPORALLY_FEASIBLE | TOO_FAST | TOO_SLOW | NO_FEASIBLE_PATH | SAME_LOCATION_STATIONARY")
    source_camera_id: str
    target_camera_id: str
    observed_delta_seconds: float
    path_exists: bool
    camera_path: List[str]
    distance_meters: float
    minimum_time_seconds: float
    maximum_reasonable_time_seconds: float
    required_average_speed_kmh: float
    speed_limit_kmh: float
    speed_ratio: float
    transition_feasibility_score: float = Field(..., ge=0.0, le=1.0)
    reid_confidence: Optional[float] = None
    explanation: str
    validation_latency_ms: float

    model_config = ConfigDict(from_attributes=True)


class SequenceObservation(BaseModel):
    """Single observation within a multi-hop vehicle journey."""
    observation_id: str
    camera_id: str
    timestamp: datetime
    plate_number: Optional[str] = None
    vehicle_color: Optional[str] = None
    vehicle_type: Optional[str] = None
    reid_confidence: Optional[float] = None


class SequenceValidationRequest(BaseModel):
    """Request to validate a chronological multi-camera journey sequence."""
    observations: List[SequenceObservation]
    congestion_tolerance_factor: float = Field(3.5, ge=1.0, le=10.0)


class SequenceValidationResponse(BaseModel):
    """Validation report across all consecutive legs of a vehicle journey."""
    total_hops: int
    feasible_hops: int
    anomalous_hops: int
    overall_route_feasible: bool
    transitions: List[TransitionValidationResponse]
    summary_explanation: str
    execution_latency_ms: float


class GraphDemoScenario(BaseModel):
    """Pre-built test scenario for demonstrating graph validation capabilities."""
    scenario_id: str
    title: str
    description: str
    source_camera_id: str
    target_camera_id: str
    source_time: str
    target_time: str
    observed_delta_seconds: float
    expected_status: str
    category: str  # FEASIBLE | TOO_FAST | CONGESTION | NO_PATH
    validation_result: TransitionValidationResponse
