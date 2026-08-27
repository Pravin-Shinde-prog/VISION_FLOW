import math
import numpy as np
from typing import Optional, List, Dict, Tuple
from app.reid.schemas import (
    VehicleVisualSignature,
    FeatureSimilarityBreakdown,
    ReIDMatchResult,
)
from app.reid.color_extractor import VehicleColorExtractor

# Vehicle Type Compatibility Matrix
TYPE_COMPATIBILITY = {
    ("sedan", "sedan"): 1.0,
    ("hatchback", "hatchback"): 1.0,
    ("suv", "suv"): 1.0,
    ("pickup", "pickup"): 1.0,
    ("van", "van"): 1.0,
    ("bus", "bus"): 1.0,
    ("truck", "truck"): 1.0,
    ("motorcycle", "motorcycle"): 1.0,

    # Perceptually related body types
    ("sedan", "hatchback"): 0.60,
    ("hatchback", "sedan"): 0.60,
    ("suv", "pickup"): 0.70,
    ("pickup", "suv"): 0.70,
    ("suv", "van"): 0.55,
    ("van", "suv"): 0.55,
}

# Baseline Feature Weights (Sum to 1.0)
DEFAULT_WEIGHTS = {
    "color": 0.25,
    "type": 0.20,
    "appearance": 0.35,
    "shape": 0.20,
}


class ReIDSimilarityCalculator:
    """
    Computes multi-feature vehicle similarity, handles missing features via dynamic weight
    renormalization, and generates natural-language match explanations.
    """

    @classmethod
    def calculate_similarity(
        cls,
        sig_a: VehicleVisualSignature,
        sig_b: VehicleVisualSignature,
        delta_time_seconds: Optional[float] = None,
        distance_meters: Optional[float] = None,
        speed_kmh: Optional[float] = None,
        is_temporally_plausible: bool = True
    ) -> ReIDMatchResult:
        # 1. Color Similarity (0.0 - 1.0)
        color_sim = VehicleColorExtractor.compute_similarity(sig_a.vehicle_color, sig_b.vehicle_color)

        # 2. Type Similarity (0.0 - 1.0)
        t_a = sig_a.vehicle_type.strip().lower() if sig_a.vehicle_type else "unknown"
        t_b = sig_b.vehicle_type.strip().lower() if sig_b.vehicle_type else "unknown"
        if t_a == "unknown" or t_b == "unknown":
            type_sim = 0.50
        elif (t_a, t_b) in TYPE_COMPATIBILITY:
            type_sim = TYPE_COMPATIBILITY[(t_a, t_b)]
        else:
            type_sim = 0.05

        # 3. Shape Similarity (Based on Aspect Ratio)
        ar_a = max(0.5, sig_a.aspect_ratio)
        ar_b = max(0.5, sig_b.aspect_ratio)
        ar_diff = abs(ar_a - ar_b) / max(ar_a, ar_b)
        shape_sim = round(max(0.0, 1.0 - ar_diff * 1.5), 3)

        # 4. Appearance Descriptor Cosine Similarity
        if sig_a.appearance_descriptor and sig_b.appearance_descriptor:
            vec_a = np.array(sig_a.appearance_descriptor, dtype=np.float32)
            vec_b = np.array(sig_b.appearance_descriptor, dtype=np.float32)
            norm_a = np.linalg.norm(vec_a)
            norm_b = np.linalg.norm(vec_b)
            if norm_a > 1e-6 and norm_b > 1e-6:
                cosine = float(np.dot(vec_a, vec_b) / (norm_a * norm_b))
                # Map [-1, 1] to [0, 1]
                app_sim = round(max(0.0, min(1.0, (cosine + 1.0) / 2.0)), 3)
            else:
                app_sim = 0.50
        else:
            # Fallback appearance approximation from color and type consistency
            app_sim = round(0.55 * color_sim + 0.45 * type_sim, 3)

        # 5. Distinctive visual markers matching
        feats_a = set(sig_a.distinctive_features)
        feats_b = set(sig_b.distinctive_features)
        if feats_a and feats_b:
            intersection = len(feats_a.intersection(feats_b))
            union = len(feats_a.union(feats_b))
            distinctive_sim = round(intersection / float(union), 3)
        elif not feats_a and not feats_b:
            distinctive_sim = 1.0
        else:
            distinctive_sim = 0.70

        # 6. Plate Number Awareness
        has_plate_a = bool(sig_a.plate_number and (sig_a.ocr_confidence or 0.0) >= 0.50)
        has_plate_b = bool(sig_b.plate_number and (sig_b.ocr_confidence or 0.0) >= 0.50)

        plate_sim: Optional[float] = None
        if has_plate_a and has_plate_b:
            # Both plates readable
            clean_a = sig_a.plate_number.replace(" ", "").upper()
            clean_b = sig_b.plate_number.replace(" ", "").upper()
            plate_sim = 1.0 if clean_a == clean_b else 0.0
            method = "PLATE_AND_VISUAL_REID"
        elif has_plate_a or has_plate_b:
            # One plate unreadable / missing -> Visual Re-ID fallback
            method = "VISUAL_REID_FALLBACK"
        else:
            # Neither plate readable -> Pure Visual Re-ID
            method = "VISUAL_REID_FALLBACK"

        # 7. Dynamic Weight Renormalization
        weights = DEFAULT_WEIGHTS.copy()
        # Compute raw weighted score
        visual_score = (
            weights["color"] * color_sim +
            weights["type"] * type_sim +
            weights["appearance"] * app_sim +
            weights["shape"] * shape_sim
        )

        # Apply plate signal if present
        if plate_sim is not None:
            if plate_sim == 1.0:
                # Strong plate identity boost
                overall_score = round(min(1.0, 0.40 * 1.0 + 0.60 * visual_score + 0.10), 3)
            else:
                # Definite plate mismatch strongly penalizes identity
                overall_score = round(0.15 * visual_score, 3)
        else:
            overall_score = round(visual_score, 3)

        # Apply temporal penalty if physically impossible
        if not is_temporally_plausible:
            overall_score = round(overall_score * 0.40, 3)

        # 8. Match Classification (Thresholds: >=0.80 HIGH, 0.60-0.79 POSSIBLE, 0.40-0.59 LOW, <0.40 NO_MATCH)
        if overall_score >= 0.80:
            classification = "HIGH_CONFIDENCE_MATCH"
            is_match = True
        elif overall_score >= 0.60:
            classification = "POSSIBLE_MATCH"
            is_match = True
        elif overall_score >= 0.40:
            classification = "LOW_CONFIDENCE"
            is_match = False
        else:
            classification = "NO_MATCH"
            is_match = False

        evidence = FeatureSimilarityBreakdown(
            color_similarity=round(color_sim, 3),
            type_similarity=round(type_sim, 3),
            appearance_similarity=round(app_sim, 3),
            shape_similarity=round(shape_sim, 3),
            plate_similarity=plate_sim,
            distinctive_features_similarity=distinctive_sim,
            weights_applied=weights
        )

        # 9. Generate Human-Readable Explanation
        explanation = cls._generate_explanation(
            classification=classification,
            overall_score=overall_score,
            evidence=evidence,
            method=method,
            sig_a=sig_a,
            sig_b=sig_b,
            delta_time=delta_time_seconds,
            distance=distance_meters,
            speed=speed_kmh,
            is_plausible=is_temporally_plausible
        )

        return ReIDMatchResult(
            is_match=is_match,
            classification=classification,
            overall_score=overall_score,
            evidence=evidence,
            delta_time_seconds=delta_time_seconds,
            distance_meters=distance_meters,
            speed_kmh=speed_kmh,
            is_temporally_plausible=is_temporally_plausible,
            method_used=method,
            explanation=explanation,
            reid_latency_ms=0.0
        )

    @classmethod
    def _generate_explanation(
        cls,
        classification: str,
        overall_score: float,
        evidence: FeatureSimilarityBreakdown,
        method: str,
        sig_a: VehicleVisualSignature,
        sig_b: VehicleVisualSignature,
        delta_time: Optional[float],
        distance: Optional[float],
        speed: Optional[float],
        is_plausible: bool
    ) -> str:
        lines = []
        status_tag = "MATCH" if overall_score >= 0.60 else "NO MATCH"
        lines.append(f"{status_tag} (Overall similarity: {int(overall_score * 100)}% - {classification.replace('_', ' ')})")
        lines.append("\nContributing Evidence:")

        # Color
        c_icon = "✓" if evidence.color_similarity >= 0.70 else "✗"
        lines.append(f"  {c_icon} Vehicle Color: {sig_a.vehicle_color.capitalize()} vs {sig_b.vehicle_color.capitalize()} ({int(evidence.color_similarity * 100)}%)")

        # Type
        t_icon = "✓" if evidence.type_similarity >= 0.70 else "✗"
        lines.append(f"  {t_icon} Vehicle Type: {sig_a.vehicle_type.upper()} vs {sig_b.vehicle_type.upper()} ({int(evidence.type_similarity * 100)}%)")

        # Appearance & Shape
        a_icon = "✓" if evidence.appearance_similarity >= 0.65 else "✗"
        lines.append(f"  {a_icon} Visual Appearance & Texture: {int(evidence.appearance_similarity * 100)}%")

        s_icon = "✓" if evidence.shape_similarity >= 0.70 else "✗"
        lines.append(f"  {s_icon} Silhouette Geometry / Aspect Ratio: {int(evidence.shape_similarity * 100)}%")

        # Spatial-temporal kinematics
        if delta_time is not None and distance is not None:
            k_icon = "✓" if is_plausible else "⚠"
            speed_str = f" @ {speed} km/h" if speed is not None else ""
            lines.append(f"  {k_icon} Kinematics: {int(delta_time)}s interval over {int(distance)}m{speed_str}")

        # Plate status
        if evidence.plate_similarity is not None:
            p_icon = "✓" if evidence.plate_similarity == 1.0 else "✗"
            lines.append(f"\nPlate: {sig_a.plate_number} vs {sig_b.plate_number} ({p_icon} Exact Plate Match)")
        else:
            lines.append("\nPlate: Unavailable / Occluded (Visual Re-ID Fallback Activated)")

        return "\n".join(lines)
