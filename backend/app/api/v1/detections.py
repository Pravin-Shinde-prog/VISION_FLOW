from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.detection import Detection
from app.models.camera import Camera
from app.models.vehicle import Vehicle
from app.schemas.detection import DetectionResponse, DetectionListResponse

router = APIRouter()


@router.get("/recent", response_model=DetectionListResponse, summary="Retrieve recent camera sightings / detections")
async def list_recent_detections(
    limit: int = Query(default=50, ge=1, le=200, description="Maximum number of detection events to return"),
    camera_id: Optional[str] = Query(None, description="Filter by camera code (e.g. CAM_PUN_001) or ID"),
    plate_number: Optional[str] = Query(None, description="Filter by license plate number"),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns the most recent camera sighting observations ordered chronologically descending.
    Supports filtering by camera node or license plate number.
    """
    query = (
        select(Detection, Camera, Vehicle)
        .join(Camera, Detection.camera_id == Camera.id)
        .outerjoin(Vehicle, Detection.vehicle_id == Vehicle.id)
        .order_by(desc(Detection.timestamp))
        .limit(limit)
    )

    if camera_id:
        if camera_id.isdigit():
            query = query.where(Detection.camera_id == int(camera_id))
        else:
            query = query.where(Camera.camera_id == camera_id.upper())

    if plate_number:
        query = query.where(Detection.plate_number.ilike(f"%{plate_number.strip()}%"))

    result = await db.execute(query)
    rows = result.all()

    items: List[DetectionResponse] = []
    for det, cam, veh in rows:
        items.append(
            DetectionResponse(
                id=det.id,
                detection_uid=det.detection_uid,
                camera_id=det.camera_id,
                camera_code=cam.camera_id,
                camera_name=cam.name,
                vehicle_id=det.vehicle_id,
                vehicle_uid=veh.vehicle_uid if veh else None,
                plate_id=det.plate_id,
                plate_number=det.plate_number,
                timestamp=det.timestamp,
                ocr_confidence=det.ocr_confidence,
                vehicle_color=det.vehicle_color,
                vehicle_type=det.vehicle_type,
                direction_travel=det.direction_travel,
                snapshot_path=det.snapshot_path,
                plate_anomaly_flags=det.plate_anomaly_flags,
                processing_metadata=det.processing_metadata,
                association_confidence=det.association_confidence,
                is_simulated=True,
                created_at=det.created_at
            )
        )

    return DetectionListResponse(total=len(items), items=items)
