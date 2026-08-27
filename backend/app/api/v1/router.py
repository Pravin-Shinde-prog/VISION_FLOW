from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.cameras import router as cameras_router

api_v1_router = APIRouter()
api_v1_router.include_router(health_router, prefix="", tags=["Health"])
api_v1_router.include_router(cameras_router, prefix="/cameras", tags=["Cameras & GIS"])
