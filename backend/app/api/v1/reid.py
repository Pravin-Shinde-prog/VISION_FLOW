from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.reid.schemas import (
    ReIDMatchRequest,
    ReIDMatchResult,
    ReIDObservationPayload,
    ReIDTrackResponse,
    ReIDDemoScenarioResponse,
)
from app.reid.engine import VehicleReIDEngine
from app.reid.demo_scenarios import ReIDDemoScenarios

router = APIRouter()


@router.post("/match", response_model=ReIDMatchResult, summary="Match two vehicle observations via multi-feature Re-ID")
async def match_vehicle_observations(
    payload: ReIDMatchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Computes explainable multi-feature similarity between two vehicle sightings.
    Integrates color, vehicle type, visual descriptors, geometry, plate evidence,
    and spatial-temporal kinematics.
    """
    engine = VehicleReIDEngine()
    result = engine.compare_observations(payload.source, payload.target)
    return result


@router.post("/track", response_model=ReIDTrackResponse, summary="Track vehicle across camera network")
async def track_vehicle_across_network(
    source_obs: ReIDObservationPayload,
    db: AsyncSession = Depends(get_db)
):
    """
    Searches recent camera detections in the database, calculates multi-feature visual similarity,
    and returns ranked candidate matches with explainable evidence.
    """
    engine = VehicleReIDEngine()
    response = await engine.track_vehicle_across_cameras(source_obs, db_session=db)
    return response


@router.get("/demo-scenario", response_model=ReIDDemoScenarioResponse, summary="Get multi-camera occluded plate tracking demonstration")
async def get_reid_demo_scenario():
    """
    Returns a reproducible multi-camera journey demonstrating continuous vehicle tracking
    when license plates become occluded by mud and glare.
    """
    return ReIDDemoScenarios.get_multi_camera_muddy_plate_scenario()
