from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class DetectionResponse(BaseModel):
    id: int
    detection_uid: str
    camera_id: int
    camera_code: str
    camera_name: str
    vehicle_id: Optional[int] = None
    vehicle_uid: Optional[str] = None
    plate_id: Optional[int] = None
    plate_number: Optional[str] = None
    timestamp: datetime
    ocr_confidence: Optional[float] = None
    vehicle_color: Optional[str] = None
    vehicle_type: Optional[str] = None
    direction_travel: Optional[str] = None
    snapshot_path: Optional[str] = None
    plate_anomaly_flags: Optional[Dict[str, Any]] = None
    processing_metadata: Optional[Dict[str, Any]] = None
    association_confidence: Optional[float] = None
    is_simulated: bool = True
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DetectionListResponse(BaseModel):
    total: int
    items: List[DetectionResponse]
