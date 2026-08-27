import cv2
import numpy as np
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.edge_vision.schemas import PreprocessingConfig
from app.edge_vision.sample_generator import SampleFrameGenerator
from app.anpr.schemas import ANPRProcessResponse, ANPRBenchmarkResponse
from app.anpr.pipeline import ANPRPipeline
from app.anpr.benchmark import ANPRBenchmarkRunner

router = APIRouter()

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp"}


@router.post("/process", response_model=ANPRProcessResponse, summary="Process frame through complete ANPR / OCR pipeline")
async def process_anpr_frame(
    file: UploadFile = File(..., description="Image frame (JPEG, PNG, WebP)"),
    camera_id: Optional[str] = Form(None, description="Camera identifier (e.g. CAM_PUN_001)"),
    enable_clahe: bool = Form(True, description="Enable CLAHE enhancement"),
    clahe_clip_limit: float = Form(2.5, description="CLAHE clip limit"),
    persist: bool = Form(False, description="Whether to persist confident detection into database"),
    db: AsyncSession = Depends(get_db)
):
    """
    Executes the complete ANPR pipeline:
    Image -> Edge Preprocessing -> Plate Detection -> OCR Character Extraction ->
    Positional Normalization -> Indian Format Validation -> Candidate Ranking.
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

    nparr = np.frombuffer(file_bytes, np.uint8)
    bgr_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if bgr_image is None or bgr_image.size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to decode image buffer. File may be corrupted."
        )

    config = PreprocessingConfig(
        enable_clahe=enable_clahe,
        clahe_clip_limit=clahe_clip_limit
    )

    pipeline = ANPRPipeline(config)
    result = await pipeline.process_frame(
        bgr_image=bgr_image,
        camera_id=camera_id or "CAM_PUN_001",
        db_session=db,
        persist=persist
    )
    return result


@router.get("/samples/{sample_id}/process", response_model=ANPRProcessResponse, summary="Process a sample scenario with ANPR")
async def process_anpr_sample(
    sample_id: str,
    camera_id: Optional[str] = Query(None, description="Camera identifier"),
    enable_clahe: bool = Query(True),
    clahe_clip_limit: float = Query(2.5),
    persist: bool = Query(False),
    db: AsyncSession = Depends(get_db)
):
    """
    Generates and processes a sample test scenario through the ANPR OCR pipeline.
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
        clahe_clip_limit=clahe_clip_limit
    )

    pipeline = ANPRPipeline(config)
    result = await pipeline.process_frame(
        bgr_image=bgr_image,
        camera_id=camera_id or "CAM_PUN_001",
        db_session=db,
        persist=persist
    )
    return result


@router.get("/benchmark", response_model=ANPRBenchmarkResponse, summary="Run automated ANPR test benchmark")
async def run_anpr_benchmark():
    """
    Executes automated benchmark evaluation across controlled sample scenarios.
    Returns exact match rate, normalized match rate, format validity rate, and average latency.
    """
    runner = ANPRBenchmarkRunner()
    return await runner.run_benchmark()
