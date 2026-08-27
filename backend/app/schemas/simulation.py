from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class SimulationRunRequest(BaseModel):
    vehicle_count: int = Field(default=30, ge=1, le=200, description="Number of synthetic vehicles to simulate")
    events_per_vehicle: int = Field(default=5, ge=1, le=20, description="Target number of camera sightings per vehicle")
    seed: Optional[int] = Field(default=42, description="Random seed for deterministic reproducibility")
    start_time: Optional[datetime] = Field(default=None, description="Starting reference timestamp (defaults to recent UTC)")


class SimulationRunResponse(BaseModel):
    status: str = "completed"
    vehicles_created: int
    plates_created: int
    events_created: int
    seed: Optional[int]
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    message: str


class SimulationStatusResponse(BaseModel):
    is_running: bool = False
    total_simulated_vehicles: int
    total_simulated_events: int
    total_simulated_plates: int
    last_run_seed: Optional[int] = None
    last_simulation_time: Optional[datetime] = None


class SimulationCleanupResponse(BaseModel):
    status: str = "cleaned"
    detections_deleted: int
    plates_deleted: int
    vehicles_deleted: int
    message: str
