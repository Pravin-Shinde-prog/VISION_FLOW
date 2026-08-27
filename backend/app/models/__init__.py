from app.models.camera import Camera
from app.models.road_edge import RoadEdge
from app.models.vehicle import Vehicle
from app.models.plate import VehiclePlate
from app.models.detection import Detection
from app.models.watchlist import Watchlist
from app.models.alert import Alert
from app.models.trajectory import Trajectory, TrajectoryEvent
from app.models.ghost_plate import GhostPlateAlert

__all__ = [
    "Camera",
    "RoadEdge",
    "Vehicle",
    "VehiclePlate",
    "Detection",
    "Watchlist",
    "Alert",
    "Trajectory",
    "TrajectoryEvent",
    "GhostPlateAlert",
]
