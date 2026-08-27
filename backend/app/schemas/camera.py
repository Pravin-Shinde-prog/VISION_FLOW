from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class CameraBase(BaseModel):
    camera_id: str = Field(..., description="Unique alphanumeric camera identifier (e.g. CAM_PUN_001)")
    name: str = Field(..., description="Descriptive human-readable camera name")
    description: Optional[str] = Field(None, description="Detailed junction or installation note")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="WGS 84 GPS Latitude")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="WGS 84 GPS Longitude")
    direction_angle: Optional[float] = Field(None, ge=0.0, le=360.0, description="Heading orientation angle in degrees (0-360)")
    road_name: Optional[str] = Field(None, description="Corridor or street name")
    sector: Optional[str] = Field(None, description="Urban zone, ward, or sector name")
    status: str = Field(default="active", description="Operational status: active, warning, offline, maintenance")
    installation_metadata: Optional[Dict[str, Any]] = Field(None, description="Mount height, resolution, FPS, streaming URI, etc.")


class CameraCreate(CameraBase):
    pass


class CameraResponse(CameraBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CameraDetailResponse(CameraResponse):
    outgoing_edges_count: int = 0
    incoming_edges_count: int = 0
    is_simulated: bool = True


class CameraListResponse(BaseModel):
    total: int
    online_count: int
    warning_count: int
    offline_count: int
    items: List[CameraResponse]


class RoadEdgeBase(BaseModel):
    source_camera_id: int
    destination_camera_id: int
    distance_meters: float = Field(..., gt=0, description="Physical distance between camera nodes in meters")
    expected_min_travel_seconds: float = Field(..., gt=0, description="Minimum feasible transit time in seconds")
    expected_max_travel_seconds: Optional[float] = Field(None, description="Maximum feasible transit time under heavy traffic")
    speed_limit_kmh: Optional[float] = Field(None, description="Speed limit in km/h")
    road_name: Optional[str] = Field(None, description="Corridor connecting the two nodes")
    direction: Optional[str] = Field(None, description="Compass direction (e.g. Northbound, Eastbound)")
    is_active: bool = True


class RoadEdgeResponse(RoadEdgeBase):
    id: int
    source_camera_code: str
    destination_camera_code: str
    source_latitude: float
    source_longitude: float
    destination_latitude: float
    destination_longitude: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoadEdgeListResponse(BaseModel):
    total: int
    items: List[RoadEdgeResponse]


class CameraNearbyResponse(CameraResponse):
    distance_from_query_meters: float
