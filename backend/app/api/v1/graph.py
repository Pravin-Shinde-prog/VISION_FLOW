from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.graph.schemas import (
    GraphTopologyResponse,
    GraphPathResponse,
    TransitionValidationRequest,
    TransitionValidationResponse,
    SequenceValidationRequest,
    SequenceValidationResponse,
    GraphDemoScenario,
)
from app.graph.engine import SpatioTemporalGraphEngine

router = APIRouter()


@router.get("/topology", response_model=GraphTopologyResponse, summary="Retrieve complete directed road network graph G=(V,E)")
async def get_graph_topology(db: AsyncSession = Depends(get_db)):
    """
    Returns the complete directed graph topology (camera nodes and road edges)
    with distances, speed limits, and minimum/maximum travel times for GIS mapping.
    """
    return await SpatioTemporalGraphEngine.get_topology(db)


@router.get("/path", response_model=GraphPathResponse, summary="Find directed shortest path between two cameras")
async def find_directed_path(
    source_camera_id: str = Query(..., description="Source Camera ID (e.g. CAM_PUN_001)"),
    target_camera_id: str = Query(..., description="Target Camera ID (e.g. CAM_PUN_004)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Executes Dijkstra's directed shortest path algorithm between two camera stations.
    Returns path node list, edge IDs, total distance, and feasible travel time boundaries.
    """
    return await SpatioTemporalGraphEngine.find_path(source_camera_id, target_camera_id, db)


@router.post("/validate-transition", response_model=TransitionValidationResponse, summary="Validate physical and temporal transition between two sightings")
async def validate_transition(
    payload: TransitionValidationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Validates physical and temporal transition between two camera observations.
    Calculates observed time delta, required average speed, speed limit ratio,
    and classifies status (TEMPORALLY_FEASIBLE, TOO_FAST, TOO_SLOW, NO_FEASIBLE_PATH).
    """
    return await SpatioTemporalGraphEngine.validate_transition(payload, db)


@router.post("/validate-sequence", response_model=SequenceValidationResponse, summary="Validate a multi-hop vehicle journey sequence")
async def validate_observation_sequence(
    payload: SequenceValidationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Validates every consecutive leg of a multi-camera vehicle trajectory (e.g. A -> B -> C -> D).
    Identifies anomalous legs and reports route-level feasibility.
    """
    return await SpatioTemporalGraphEngine.validate_sequence(payload, db)


@router.get("/demo-scenarios", response_model=List[GraphDemoScenario], summary="Retrieve pre-built Spatio-Temporal Graph demonstration scenarios")
async def get_graph_demo_scenarios(db: AsyncSession = Depends(get_db)):
    """
    Returns pre-configured scenarios demonstrating:
    1. Realistic Feasible Transit
    2. Impossible High-Speed Movement (TOO_FAST)
    3. Severe Congestion Delay (TOO_SLOW)
    4. Topologically Disconnected Cameras (NO_FEASIBLE_PATH)
    """
    return await SpatioTemporalGraphEngine.get_demo_scenarios(db)
