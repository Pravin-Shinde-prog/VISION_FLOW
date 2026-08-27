from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, text, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.db.session import get_db
from app.models.camera import Camera
from app.models.road_edge import RoadEdge
from app.schemas.camera import (
    CameraResponse,
    CameraDetailResponse,
    CameraListResponse,
    RoadEdgeResponse,
    RoadEdgeListResponse,
    CameraNearbyResponse
)

router = APIRouter()


@router.get("", response_model=CameraListResponse, summary="Retrieve all cameras in the network")
async def list_cameras(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (active, warning, offline)"),
    sector_filter: Optional[str] = Query(None, alias="sector", description="Filter by sector or urban zone"),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns all registered cameras in the city-wide ANPR/CCTV network.
    Includes operational status counts and GPS coordinates.
    """
    query = select(Camera).order_by(Camera.camera_id)
    if status_filter:
        query = query.where(Camera.status == status_filter.lower())
    if sector_filter:
        query = query.where(Camera.sector.ilike(f"%{sector_filter}%"))

    result = await db.execute(query)
    cameras = result.scalars().all()

    # Calculate status aggregates
    all_cams_result = await db.execute(select(Camera.status))
    all_statuses = [s[0].lower() for s in all_cams_result.fetchall()]

    online_cnt = sum(1 for s in all_statuses if s in ("active", "online"))
    warning_cnt = sum(1 for s in all_statuses if s == "warning")
    offline_cnt = sum(1 for s in all_statuses if s in ("offline", "maintenance"))

    return CameraListResponse(
        total=len(cameras),
        online_count=online_cnt,
        warning_count=warning_cnt,
        offline_count=offline_cnt,
        items=[CameraResponse.model_validate(c) for c in cameras]
    )


@router.get("/edges", response_model=RoadEdgeListResponse, summary="Retrieve directed road graph connections")
async def list_road_edges(
    is_active_only: bool = Query(True, description="Filter for active road connections only"),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns all directed road connections (Camera A -> Camera B) with travel metrics,
    distances, speed limits, and node GPS coordinates for GIS polyline rendering.
    """
    source_cam = aliased(Camera, name="src_cam")
    dest_cam = aliased(Camera, name="dst_cam")

    query = (
        select(
            RoadEdge,
            source_cam.camera_id.label("src_code"),
            source_cam.latitude.label("src_lat"),
            source_cam.longitude.label("src_lon"),
            dest_cam.camera_id.label("dst_code"),
            dest_cam.latitude.label("dst_lat"),
            dest_cam.longitude.label("dst_lon"),
        )
        .join(source_cam, RoadEdge.source_camera_id == source_cam.id)
        .join(dest_cam, RoadEdge.destination_camera_id == dest_cam.id)
        .order_by(RoadEdge.id)
    )

    if is_active_only:
        query = query.where(RoadEdge.is_active.is_(True))

    result = await db.execute(query)
    rows = result.all()

    items: List[RoadEdgeResponse] = []
    for edge, src_code, src_lat, src_lon, dst_code, dst_lat, dst_lon in rows:
        items.append(
            RoadEdgeResponse(
                id=edge.id,
                source_camera_id=edge.source_camera_id,
                destination_camera_id=edge.destination_camera_id,
                source_camera_code=src_code,
                destination_camera_code=dst_code,
                source_latitude=src_lat,
                source_longitude=src_lon,
                destination_latitude=dst_lat,
                destination_longitude=dst_lon,
                distance_meters=edge.distance_meters,
                expected_min_travel_seconds=edge.expected_min_travel_seconds,
                expected_max_travel_seconds=edge.expected_max_travel_seconds,
                speed_limit_kmh=edge.speed_limit_kmh,
                road_name=edge.road_name,
                direction=edge.direction,
                is_active=edge.is_active,
                created_at=edge.created_at
            )
        )

    return RoadEdgeListResponse(total=len(items), items=items)


@router.get("/nearby", response_model=List[CameraNearbyResponse], summary="Find cameras within a geographic radius")
async def find_nearby_cameras(
    latitude: float = Query(..., ge=-90.0, le=90.0, description="Center Latitude"),
    longitude: float = Query(..., ge=-180.0, le=180.0, description="Center Longitude"),
    radius_km: float = Query(5.0, gt=0, le=50.0, description="Search radius in kilometers"),
    db: AsyncSession = Depends(get_db)
):
    """
    Executes a PostGIS spatial query (ST_DWithin on WGS 84 geography) to find all cameras
    within the specified geographic radius from the query point.
    """
    radius_meters = radius_km * 1000.0

    # PostGIS ST_DWithin and ST_Distance calculation on geography type
    spatial_sql = text("""
        SELECT 
            id, camera_id, name, description, latitude, longitude,
            direction_angle, road_name, sector, status, installation_metadata,
            created_at, updated_at,
            ST_Distance(location::geography, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography) AS dist_meters
        FROM cameras
        WHERE ST_DWithin(location::geography, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography, :radius)
        ORDER BY dist_meters ASC;
    """)

    result = await db.execute(
        spatial_sql,
        {"lat": latitude, "lon": longitude, "radius": radius_meters}
    )
    rows = result.fetchall()

    nearby_cameras: List[CameraNearbyResponse] = []
    for r in rows:
        nearby_cameras.append(
            CameraNearbyResponse(
                id=r.id,
                camera_id=r.camera_id,
                name=r.name,
                description=r.description,
                latitude=r.latitude,
                longitude=r.longitude,
                direction_angle=r.direction_angle,
                road_name=r.road_name,
                sector=r.sector,
                status=r.status,
                installation_metadata=r.installation_metadata,
                created_at=r.created_at,
                updated_at=r.updated_at,
                distance_from_query_meters=round(r.dist_meters, 2)
            )
        )

    return nearby_cameras


@router.get("/{camera_id}", response_model=CameraDetailResponse, summary="Get details for a specific camera")
async def get_camera_by_id(
    camera_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves complete camera metadata, connected edge counts, and operational parameters.
    Accepts alphanumeric camera_id (e.g. CAM_PUN_001) or primary key ID.
    """
    query = select(Camera).where(
        or_(
            Camera.camera_id == camera_id,
            Camera.camera_id == camera_id.upper(),
            Camera.id == int(camera_id) if camera_id.isdigit() else False
        )
    )

    result = await db.execute(query)
    camera = result.scalars().first()

    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera with identifier '{camera_id}' not found."
        )

    # Edge counts
    out_cnt = len(camera.outgoing_edges) if camera.outgoing_edges else 0
    in_cnt = len(camera.incoming_edges) if camera.incoming_edges else 0

    return CameraDetailResponse(
        id=camera.id,
        camera_id=camera.camera_id,
        name=camera.name,
        description=camera.description,
        latitude=camera.latitude,
        longitude=camera.longitude,
        direction_angle=camera.direction_angle,
        road_name=camera.road_name,
        sector=camera.sector,
        status=camera.status,
        installation_metadata=camera.installation_metadata,
        created_at=camera.created_at,
        updated_at=camera.updated_at,
        outgoing_edges_count=out_cnt,
        incoming_edges_count=in_cnt,
        is_simulated=True
    )
