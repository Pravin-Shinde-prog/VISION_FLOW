import time
from typing import List, Dict, Any
from app.edge_vision.sample_generator import SampleFrameGenerator
from app.anpr.pipeline import ANPRPipeline
from app.anpr.schemas import ANPRBenchmarkResponse


BENCHMARK_SCENARIOS = [
    {
        "sample_id": "clean_hsrp_day",
        "title": "Standard HSRP (Daytime)",
        "expected_plate": "MH12AB1234",
        "expected_valid": True,
        "category": "Optimal Lighting",
    },
    {
        "sample_id": "night_glare",
        "title": "Night Headlight Glare",
        "expected_plate": None,
        "expected_valid": False,
        "category": "Adverse Lighting",
    },
    {
        "sample_id": "rain_motion_blur",
        "title": "Monsoon Rain & Motion Blur",
        "expected_plate": None,
        "expected_valid": False,
        "category": "Adverse Weather",
    },
    {
        "sample_id": "damaged_cracked_plate",
        "title": "Damaged / Cracked Plate",
        "expected_plate": "MH12AB1234",
        "expected_valid": True,
        "category": "Compliance Anomaly",
    },
    {
        "sample_id": "mud_occluded_plate",
        "title": "Mud / Dirt Occluded Plate",
        "expected_plate": None,
        "expected_valid": False,
        "category": "Occlusion",
    },
]


class ANPRBenchmarkRunner:
    """
    Executes a reproducible evaluation benchmark over controlled sample test scenarios.
    Measures exact match rate, normalized match rate, format validation rate, and latency.
    """

    def __init__(self):
        self.pipeline = ANPRPipeline()

    async def run_benchmark(self) -> ANPRBenchmarkResponse:
        total = len(BENCHMARK_SCENARIOS)
        exact_matches = 0
        normalized_matches = 0
        format_valid_count = 0
        latencies = []
        breakdown: List[Dict[str, Any]] = []

        for item in BENCHMARK_SCENARIOS:
            sid = item["sample_id"]
            img = SampleFrameGenerator.generate_sample_image(sid)

            t0 = time.perf_counter()
            res = await self.pipeline.process_frame(img, camera_id="CAM_PUN_001")
            lat = round((time.perf_counter() - t0) * 1000, 2)
            latencies.append(lat)

            primary = res.primary_plate
            ocr_res = primary.ocr_result if primary else None
            extracted_raw = ocr_res.raw_text if ocr_res else None
            extracted_norm = ocr_res.normalized_plate if ocr_res else None
            is_valid = ocr_res.format_valid if ocr_res else False

            # Evaluation metrics
            expected = item["expected_plate"]

            if expected is None:
                # Should correctly reject or report unreadable
                is_exact = extracted_norm is None
                is_norm = extracted_norm is None
            else:
                is_exact = extracted_raw == expected
                is_norm = extracted_norm == expected

            if is_exact:
                exact_matches += 1
            if is_norm:
                normalized_matches += 1
            if is_valid == item["expected_valid"]:
                format_valid_count += 1

            breakdown.append({
                "sample_id": sid,
                "title": item["title"],
                "category": item["category"],
                "expected_plate": expected,
                "raw_extracted": extracted_raw,
                "normalized_extracted": extracted_norm,
                "format_valid": is_valid,
                "exact_match": is_exact,
                "normalized_match": is_norm,
                "latency_ms": lat,
                "readability": ocr_res.readability if ocr_res else "UNREADABLE",
                "final_confidence": ocr_res.final_confidence if ocr_res else 0.0,
            })

        avg_lat = round(sum(latencies) / float(len(latencies)), 2) if latencies else 0.0

        return ANPRBenchmarkResponse(
            total_samples=total,
            exact_matches=exact_matches,
            exact_match_rate=round(exact_matches / float(total), 3),
            normalized_matches=normalized_matches,
            normalized_match_rate=round(normalized_matches / float(total), 3),
            format_valid_count=format_valid_count,
            format_valid_rate=round(format_valid_count / float(total), 3),
            average_latency_ms=avg_lat,
            results_breakdown=breakdown,
            disclaimer="Prototype benchmark on controlled test scenarios — not representative of real-world multi-lane field accuracy."
        )
