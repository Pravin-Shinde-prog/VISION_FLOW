from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.cameras import router as cameras_router
from app.api.v1.detections import router as detections_router
from app.api.v1.simulation import router as simulation_router
from app.api.v1.edge_vision import router as edge_vision_router
from app.api.v1.anpr import router as anpr_router
from app.api.v1.reid import router as reid_router
from app.api.v1.graph import router as graph_router
from app.api.v1.ghost_plates import router as ghost_plates_router

api_v1_router = APIRouter()
api_v1_router.include_router(health_router, prefix="", tags=["Health"])
api_v1_router.include_router(cameras_router, prefix="/cameras", tags=["Cameras & GIS"])
api_v1_router.include_router(detections_router, prefix="/detections", tags=["Detections & Sightings"])
api_v1_router.include_router(simulation_router, prefix="/simulation", tags=["Synthetic Traffic Simulator"])
api_v1_router.include_router(edge_vision_router, prefix="/edge-vision", tags=["Smart Edge Vision & Preprocessing"])
api_v1_router.include_router(anpr_router, prefix="/anpr", tags=["ANPR & License Plate OCR"])
api_v1_router.include_router(reid_router, prefix="/reid", tags=["Multi-Feature Vehicle Re-ID"])
api_v1_router.include_router(graph_router, prefix="/graph", tags=["Spatio-Temporal Graph Engine"])
api_v1_router.include_router(ghost_plates_router, prefix="/ghost-plates", tags=["Ghost / Cloned Plate Detection"])
