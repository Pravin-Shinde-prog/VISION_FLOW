import pytest
import io
import cv2
import httpx
import onnxruntime as ort
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.anpr.validator import IndianPlateValidator
from app.anpr.normalizer import IndianPlateNormalizer
from app.anpr.engine import PlateOCREngine
from app.anpr.pipeline import ANPRPipeline
from app.anpr.benchmark import ANPRBenchmarkRunner
from app.edge_vision.sample_generator import SampleFrameGenerator
from app.edge_vision.plate_detector import PlateRegionDetector
from app.models.detection import Detection
from app.main import app


def test_onnx_model_execution_and_session_properties():
    """Verify that ONNX Runtime InferenceSession loads the real model and executes on CPU."""
    engine = PlateOCREngine()

    # 1. Assert session structure
    assert engine._session is not None
    assert isinstance(engine._session, ort.InferenceSession)
    assert "CPUExecutionProvider" in engine._session.get_providers()

    inputs = engine._session.get_inputs()
    assert len(inputs) == 1
    assert inputs[0].name == "x"
    assert inputs[0].type == "tensor(float)"

    outputs = engine._session.get_outputs()
    assert len(outputs) == 1
    assert outputs[0].name == "softmax_2.tmp_0"
    assert outputs[0].type == "tensor(float)"

    # 2. Execute on crop
    frame = SampleFrameGenerator.generate_sample_image("clean_hsrp_day")
    cands = PlateRegionDetector().detect_candidate_regions(frame)
    assert len(cands) > 0
    crop = cands[0]["cropped_bgr"]

    result = engine.recognize_plate(crop, plate_quality=0.88)
    assert result.ocr_engine == "ONNX-PP-OCRv4"
    assert result.raw_text != ""
    assert result.normalized_plate == "MH12AB1234"
    assert result.format_valid is True
    assert result.ocr_confidence > 0.70
    assert result.ocr_latency_ms > 0


def test_indian_plate_validator():
    """Verify Indian RTO standard HSRP and Bharat series validation."""
    validator = IndianPlateValidator()

    # Valid HSRP
    v1 = validator.validate("MH12AB1234")
    assert v1.is_valid is True
    assert v1.format_type == "standard_hsrp"
    assert v1.components.state_code == "MH"
    assert v1.components.district_code == "12"
    assert v1.components.series == "AB"
    assert v1.components.registration_number == "1234"

    # Valid Bharat series
    v2 = validator.validate("22BH1234AA")
    assert v2.is_valid is True
    assert v2.format_type == "bharat_series"

    # Invalid state code
    v3 = validator.validate("ZZ12AB1234")
    assert v3.is_valid is False

    # Malformed / garbage
    v4 = validator.validate("INVALID_PLATE_123")
    assert v4.is_valid is False


def test_indian_plate_normalizer():
    """Verify positional character optical confusion normalization."""
    normalizer = IndianPlateNormalizer()

    # 1. Number digit 'I' in place of '1'
    res1 = normalizer.normalize("MH12ABI234")
    assert res1.normalized_plate == "MH12AB1234"
    assert res1.is_normalized is True

    # 2. District digit 'Z' in place of '2'
    res2 = normalizer.normalize("MH1ZAB1234")
    assert res2.normalized_plate == "MH12AB1234"
    assert res2.is_normalized is True

    # 3. Series letter '8' in place of 'B'
    res3 = normalizer.normalize("MH12A81234")
    assert res3.normalized_plate == "MH12AB1234"
    assert res3.is_normalized is True

    # 4. Clean plate requires no change
    res4 = normalizer.normalize("MH12AB1234")
    assert res4.normalized_plate == "MH12AB1234"
    assert res4.is_normalized is False


@pytest.mark.anyio
async def test_anpr_pipeline_and_benchmark(db_session: AsyncSession):
    """Verify end-to-end pipeline execution and benchmark suite."""
    pipeline = ANPRPipeline()
    frame = SampleFrameGenerator.generate_sample_image("clean_hsrp_day")

    res = await pipeline.process_frame(frame, camera_id="CAM_PUN_001")
    assert res.plate_detected is True
    assert res.primary_plate is not None
    assert res.primary_plate.ocr_result.normalized_plate == "MH12AB1234"
    assert res.primary_plate.ocr_result.format_valid is True
    assert res.total_latency_ms > 0

    # Run Benchmark
    benchmark_runner = ANPRBenchmarkRunner()
    bench_res = await benchmark_runner.run_benchmark()
    assert bench_res.total_samples == 5
    assert bench_res.normalized_match_rate >= 0.80
    assert bench_res.average_latency_ms > 0


@pytest.mark.anyio
async def test_anpr_api_endpoints_and_persistence(db_session: AsyncSession):
    """Verify ANPR HTTP endpoints and database persistence mode."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # 1. Process sample scenario
        sample_res = await client.get("/api/v1/anpr/samples/clean_hsrp_day/process")
        assert sample_res.status_code == 200
        data = sample_res.json()
        assert data["data_source"] == "anpr_engine"
        assert data["plate_detected"] is True
        assert data["primary_plate"]["ocr_result"]["normalized_plate"] == "MH12AB1234"

        # 2. Run Benchmark via API
        bench_res = await client.get("/api/v1/anpr/benchmark")
        assert bench_res.status_code == 200
        bench_data = bench_res.json()
        assert bench_data["total_samples"] == 5

        # 3. Process via file upload with persist=true
        test_img = SampleFrameGenerator.generate_sample_image("clean_hsrp_day")
        _, img_bytes = cv2.imencode(".jpg", test_img)
        files = {"file": ("plate_test.jpg", io.BytesIO(img_bytes.tobytes()), "image/jpeg")}

        upload_res = await client.post(
            "/api/v1/anpr/process",
            files=files,
            data={"camera_id": "CAM_PUN_001", "persist": "true"}
        )
        assert upload_res.status_code == 200
        upload_data = upload_res.json()
        assert upload_data["persisted_detection_id"] is not None
