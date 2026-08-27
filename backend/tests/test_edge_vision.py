import pytest
import io
import cv2
import numpy as np
import httpx

from app.edge_vision.schemas import PreprocessingConfig
from app.edge_vision.preprocessing import ImagePreprocessor
from app.edge_vision.quality import ImageQualityAnalyzer
from app.edge_vision.plate_detector import PlateRegionDetector
from app.edge_vision.pipeline import EdgeVisionPipeline
from app.edge_vision.sample_generator import SampleFrameGenerator
from app.main import app


def test_image_preprocessor_enhancement():
    """Verify CLAHE, sharpening, and edge map extraction."""
    test_img = np.zeros((300, 400, 3), dtype=np.uint8)
    test_img[:, :, 0] = np.linspace(30, 200, 400, dtype=np.uint8)
    test_img[:, :, 1] = 100
    test_img[:, :, 2] = 120

    preprocessor = ImagePreprocessor()
    enhanced = preprocessor.enhance_frame(test_img)

    assert enhanced.shape == test_img.shape
    assert enhanced.dtype == np.uint8

    gray = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
    edge_map = preprocessor.extract_edge_representation(gray)
    assert edge_map.shape == gray.shape
    assert edge_map.dtype == np.uint8


def test_image_quality_analyzer_metrics():
    """Verify metric bounds and sensitivity to blur, glare, and contrast."""
    analyzer = ImageQualityAnalyzer()

    # 1. Normal contrast image
    normal_img = np.random.randint(80, 180, (200, 200, 3), dtype=np.uint8)
    metrics_normal = analyzer.analyze(normal_img)

    assert 0.0 <= metrics_normal.brightness_score <= 1.0
    assert 0.0 <= metrics_normal.contrast_score <= 1.0
    assert 0.0 <= metrics_normal.sharpness_score <= 1.0
    assert 0.0 <= metrics_normal.glare_score <= 1.0
    assert 0.0 <= metrics_normal.overall_quality_score <= 1.0

    # 2. Glare test (mostly saturated 255)
    glare_img = np.ones((200, 200, 3), dtype=np.uint8) * 255
    metrics_glare = analyzer.analyze(glare_img)
    assert metrics_glare.glare_score > 0.80

    # 3. Blur test (flat uniform image vs high-frequency sharp image)
    flat_img = np.ones((200, 200, 3), dtype=np.uint8) * 128
    metrics_flat = analyzer.analyze(flat_img)

    sharp_img = np.zeros((200, 200, 3), dtype=np.uint8)
    sharp_img[::4, :] = 255
    metrics_sharp = analyzer.analyze(sharp_img)

    assert metrics_sharp.sharpness_score > metrics_flat.sharpness_score


def test_plate_condition_and_anomaly_evaluation():
    """Verify condition classification across sample scenarios."""
    pipeline = EdgeVisionPipeline()

    # 1. Clean Daytime HSRP
    clean_frame = SampleFrameGenerator.generate_sample_image("clean_hsrp_day")
    res_clean = pipeline.process_image(clean_frame, camera_id="CAM_PUN_001")

    assert res_clean.plate_detected is True
    assert res_clean.primary_plate is not None
    assert res_clean.primary_plate.condition == "NORMAL"
    assert res_clean.primary_plate.anomaly_flags.missing_plate is False
    assert res_clean.processing_latency_ms > 0

    # 2. Night Glare Scenario (Extreme glare obscuring front bumper)
    glare_frame = SampleFrameGenerator.generate_sample_image("night_glare")
    res_glare = pipeline.process_image(glare_frame, camera_id="CAM_PUN_002")
    # Overall image has glare and flags anomaly
    assert res_glare.image_quality.glare_score > 0.15
    assert res_glare.overall_anomaly_detected is True


@pytest.mark.anyio
async def test_edge_vision_api_endpoints():
    """Verify HTTP endpoints for edge vision processing and sample catalog."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # 1. List samples catalog
        samples_res = await client.get("/api/v1/edge-vision/samples")
        assert samples_res.status_code == 200
        samples = samples_res.json()
        assert len(samples) >= 5
        sample_ids = [s["sample_id"] for s in samples]
        assert "clean_hsrp_day" in sample_ids
        assert "night_glare" in sample_ids

        # 2. Process sample scenario on-demand
        proc_sample_res = await client.get("/api/v1/edge-vision/samples/clean_hsrp_day/process")
        assert proc_sample_res.status_code == 200
        proc_data = proc_sample_res.json()
        assert proc_data["data_source"] == "edge_vision"
        assert proc_data["pipeline_version"] == "edge_v1.0"
        assert "image_quality" in proc_data
        assert proc_data["plate_detected"] is True
        assert proc_data["enhanced_frame_b64"] is not None

        # 3. Process via multipart file upload
        test_img = SampleFrameGenerator.generate_sample_image("clean_hsrp_day")
        _, img_bytes = cv2.imencode(".jpg", test_img)
        files = {"file": ("test_frame.jpg", io.BytesIO(img_bytes.tobytes()), "image/jpeg")}

        upload_res = await client.post(
            "/api/v1/edge-vision/process",
            files=files,
            data={"camera_id": "CAM_PUN_005", "enable_clahe": "true"}
        )
        assert upload_res.status_code == 200
        upload_data = upload_res.json()
        assert upload_data["camera_id"] == "CAM_PUN_005"
        assert upload_data["plate_detected"] is True

        # 4. Invalid file upload error handling
        bad_files = {"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")}
        bad_res = await client.post("/api/v1/edge-vision/process", files=bad_files)
        assert bad_res.status_code == 400
