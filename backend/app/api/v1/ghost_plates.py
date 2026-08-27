from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.ghost_plates.schemas import (
    GhostPlateAnalysisRequest,
    GhostPlateAlertRecord,
    LiveSightingEvaluationRequest,
    LiveSightingEvaluationResponse,
    GhostPlateStatusUpdate,
    GhostPlateScenario,
)
from app.ghost_plates.engine import GhostPlateEngine

router = APIRouter()


@router.post("/analyze", response_model=GhostPlateAlertRecord, summary="Analyze pairwise plate sightings for cloning / ghost anomaly")
async def analyze_sighting_pair(
    payload: GhostPlateAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyzes physical/topological feasibility between two sightings of the same license plate.
    Evaluates speed, minimum travel time, OCR confidence, and Re-ID agreement.
    """
    return await GhostPlateEngine.analyze_transition(payload, db)


@router.post("/evaluate-sighting", response_model=LiveSightingEvaluationResponse, summary="Evaluate incoming live plate sighting against recent history")
async def evaluate_live_sighting(
    payload: LiveSightingEvaluationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Evaluates a newly arrived plate sighting against previous database sightings,
    detects impossible travel anomalies, and automatically creates alert records if suspicious.
    """
    return await GhostPlateEngine.evaluate_live_sighting(payload, db)


@router.get("/alerts", response_model=List[GhostPlateAlertRecord], summary="List recent Ghost Plate alerts")
async def list_ghost_plate_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity: CRITICAL, HIGH, MEDIUM, LOW"),
    status: Optional[str] = Query(None, description="Filter by review status: NEW, REVIEWED, DISMISSED, CONFIRMED_BY_OPERATOR"),
    plate_number: Optional[str] = Query(None, description="Filter by license plate number"),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves stored ghost plate alerts with optional filtering by severity, review status, and plate.
    """
    return await GhostPlateEngine.list_alerts(db, severity=severity, status=status, plate_number=plate_number, limit=limit)


@router.get("/alerts/{alert_id}", response_model=GhostPlateAlertRecord, summary="Get forensic details for a specific Ghost Plate alert")
async def get_ghost_plate_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves complete evidence details and dual-snapshot references for a specific alert.
    """
    alerts = await GhostPlateEngine.list_alerts(db, limit=100)
    for a in alerts:
        if a.alert_id == alert_id:
            return a
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Alert with ID '{alert_id}' not found.")


@router.patch("/alerts/{alert_id}", response_model=GhostPlateAlertRecord, summary="Update Ghost Plate alert review status")
async def update_alert_review_status(
    alert_id: str,
    payload: GhostPlateStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Updates operator review status (REVIEWED, DISMISSED, CONFIRMED_BY_OPERATOR) and notes.
    """
    updated = await GhostPlateEngine.update_alert_status(alert_id, payload, db)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Alert with ID '{alert_id}' not found.")
    return updated


@router.get("/demo-scenarios", response_model=List[GhostPlateScenario], summary="Retrieve 5 reproducible Ghost Plate test scenarios")
async def get_ghost_plate_scenarios(db: AsyncSession = Depends(get_db)):
    """
    Returns 5 pre-configured demonstration scenarios:
    1. Normal Movement (No Anomaly)
    2. Impossible Speed (Possible Cloned Plate - CRITICAL)
    3. No Directed Path (Topology Inconsistent - HIGH)
    4. Low OCR Confidence Sighting (LOW)
    5. Same Camera Repeat (Normal Repeat Sighting)
    """
    return await GhostPlateEngine.get_demo_scenarios(db)
