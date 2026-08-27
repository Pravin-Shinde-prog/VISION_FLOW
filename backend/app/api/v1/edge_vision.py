import cv2
import numpy as np
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Query
from app.edge_vision.schemas import (
    EdgeVisionProcessResponse,
    PreprocessingConfig,
    SampleFrameInfo
)
from app.edge_vision.pipeline import EdgeVisionPipeline
from app.edge_vision.sample_generator import SampleFrameGenerator

router = APIRouter()

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp"}


@router.post("/process", response_model=EdgeVisionProcessResponse, summary="Process uploaded image frame through Edge Vision pipeline")
async def process_frame(
    file: UploadFile = File(..., description="Image frame (JPEG, PNG, WebP)"),
    camera_id: Optional[str] = Form(None, description="Optional camera ID (e.g. CAM_PUN_001)"),
    enable_clahe: bool = Form(True, description="Enable CLAHE contrast enhancement"),
    clahe_clip_limit: float = Form(2.5, description="CLAHE clip limit (1.0 - 10.0)"),
    enable_denoising: bool = Form(True, description="Enable bilateral edge-preserving smoothing"),
    enable_sharpening: bool = Form(True, description="Enable unsharp masking"),
    sharpen_strength: float = Form(0.5, description="Sharpening strength (0.0 - 2.0)"),
    enable_glare_reduction: bool = Form(True, description="Enable glare/shadow compensation")
):
    """
    Accepts an uploaded image frame and executes the Edge Vision preprocessing, quality evaluation,
    plate candidate localization, and rule-based anomaly detection pipeline.
    """
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{file.content_type}'. Allowed types: JPEG, PNG, WebP, BMP."
        )

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes)."
        )

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024*1024)} MB."
        )

    # Decode image buffer to BGR
    nparr = np.frombuffer(file_bytes, np.uint8)
    bgr_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if bgr_image is None or bgr_image.size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to decode image. File may be corrupted or invalid."
        )

    # Build Preprocessing Configuration
    config = PreprocessingConfig(
        enable_clahe=enable_clahe,
        clahe_clip_limit=clahe_clip_limit,
        enable_denoising=enable_denoising,
        enable_sharpening=enable_sharpening,
        sharpen_strength=sharpen_strength,
        enable_glare_reduction=enable_glare_reduction
    )

    pipeline = EdgeVisionPipeline(config)
    result = pipeline.process_image(bgr_image, camera_id=camera_id)
    return result


@router.get("/samples", response_model=List[SampleFrameInfo], summary="List available development test frame scenarios")
async def list_sample_frames():
    """
    Returns a catalog of built-in test scenarios (Clean HSRP, Night Glare, Rain Blur, Damaged, Mud Occluded)
    for quick developer inspection.
    """
    return SampleFrameGenerator.get_sample_catalog()


@router.get("/samples/{sample_id}/process", response_model=EdgeVisionProcessResponse, summary="Process a built-in test scenario")
async def process_sample_frame(
    sample_id: str,
    camera_id: Optional[str] = Query(None, description="Optional camera ID"),
    enable_clahe: bool = Query(True),
    clahe_clip_limit: float = Query(2.5),
    enable_denoising: bool = Query(True),
    enable_sharpening: bool = Query(True),
    sharpen_strength: float = Query(0.5),
    enable_glare_reduction: bool = Query(True)
):
    """
    Generates and processes a synthetic test frame scenario on-demand.
    """
    catalog = {s.sample_id for s in SampleFrameGenerator.get_sample_catalog()}
    if sample_id not in catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sample scenario '{sample_id}' not found. Available: {list(catalog)}"
        )

    bgr_image = SampleFrameGenerator.generate_sample_image(sample_id)

    config = PreprocessingConfig(
        enable_clahe=enable_clahe,
        clahe_clip_limit=clahe_clip_limit,
        enable_denoising=enable_denoising,
        enable_sharpening=enable_sharpening,
        sharpen_strength=sharpen_strength,
        enable_glare_reduction=enable_glare_reduction
    )

    pipeline = EdgeVisionPipeline(config)
    result = pipeline.process_image(bgr_image, camera_id=camera_id or "CAM_PUN_001")
    return result
