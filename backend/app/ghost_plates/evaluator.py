import math
from typing import List, Tuple, Optional
from app.ghost_plates.schemas import EvidenceItem, GhostPlateAlertRecord


class GhostPlateEvaluator:
    """
    Computes explainable anomaly evidence score, severity level,
    and structured forensic evidence checklist for suspected ghost/cloned plates.
    """

    @classmethod
    def evaluate_anomaly(
        cls,
        plate_normalized: str,
        source_camera_id: str,
        target_camera_id: str,
        ocr_conf_source: float,
        ocr_conf_target: float,
        graph_status: str,
        observed_delta_seconds: float,
        minimum_feasible_time_seconds: float,
        distance_meters: float,
        required_speed_kmh: float,
        speed_limit_kmh: float,
        reid_similarity: Optional[float] = None
    ) -> Tuple[str, str, float, List[EvidenceItem], str]:
        """
        Returns (alert_type, severity, anomaly_score, evidence_checklist, explanation)
        """
        evidence_checklist: List[EvidenceItem] = []

        # 1. Plate Evidence
        evidence_checklist.append(
            EvidenceItem(
                category="PLATE_EVIDENCE",
                verdict="CONSISTENT",
                description=f"Identical normalized Indian plate string: '{plate_normalized}' observed at both stations.",
                severity_impact=0.20
            )
        )

        # 2. Case: Same Camera Repeat Sighting
        if source_camera_id.upper() == target_camera_id.upper():
            evidence_checklist.append(
                EvidenceItem(
                    category="SPATIAL_EVIDENCE",
                    verdict="NORMAL",
                    description=f"Sighted repeatedly at the same camera station ({source_camera_id}). Stationary/loitering vehicle.",
                    severity_impact=0.0
                )
            )
            return (
                "NORMAL_REPEAT_SIGHTING",
                "NONE",
                0.0,
                evidence_checklist,
                f"Vehicle '{plate_normalized}' observed repeatedly at same station {source_camera_id} across {int(observed_delta_seconds)}s. No movement anomaly."
            )

        # 3. OCR Confidence Product C_ocr = sqrt(conf_A * conf_B)
        ocr_prod = math.sqrt(max(0.1, min(1.0, ocr_conf_source)) * max(0.1, min(1.0, ocr_conf_target)))
        if ocr_prod < 0.70:
            evidence_checklist.append(
                EvidenceItem(
                    category="PLATE_EVIDENCE",
                    verdict="INCONCLUSIVE",
                    description=f"Moderate/low OCR confidence (Source: {int(ocr_conf_source*100)}%, Target: {int(ocr_conf_target*100)}%). Plate confusion possible.",
                    severity_impact=0.25
                )
            )

        # 4. Spatial & Kinematics Evidence
        dist_km = round(distance_meters / 1000.0, 2)
        speed_ratio = round(required_speed_kmh / max(10.0, speed_limit_kmh), 2)

        # Base Anomaly Factors
        s_kin = 0.0
        s_topo = 0.0
        s_reid = 0.0

        if graph_status == "TOO_FAST":
            # Kinematic impossibility
            if required_speed_kmh > 400.0 or speed_ratio > 4.0:
                s_kin = 1.0
            elif speed_ratio > 2.5:
                s_kin = 0.90
            elif speed_ratio > 1.5:
                s_kin = 0.75
            else:
                s_kin = 0.60

            evidence_checklist.append(
                EvidenceItem(
                    category="KINEMATIC_EVIDENCE",
                    verdict="CONTRADICTORY",
                    description=f"Required average speed of {required_speed_kmh} km/h exceeds {speed_limit_kmh} km/h speed limit ({speed_ratio}x). Observed {int(observed_delta_seconds)}s vs min feasible {int(minimum_feasible_time_seconds)}s.",
                    severity_impact=0.55
                )
            )
            evidence_checklist.append(
                EvidenceItem(
                    category="TEMPORAL_EVIDENCE",
                    verdict="CONTRADICTORY",
                    description=f"Transit completed {int(minimum_feasible_time_seconds - observed_delta_seconds)}s faster than physically allowed by road topology.",
                    severity_impact=0.35
                )
            )

        elif graph_status == "NO_FEASIBLE_PATH":
            s_topo = 0.90
            evidence_checklist.append(
                EvidenceItem(
                    category="SPATIAL_EVIDENCE",
                    verdict="CONTRADICTORY",
                    description=f"No directed road connection exists in Pune road network between {source_camera_id} and {target_camera_id}.",
                    severity_impact=0.45
                )
            )

        elif graph_status == "TEMPORALLY_FEASIBLE":
            evidence_checklist.append(
                EvidenceItem(
                    category="KINEMATIC_EVIDENCE",
                    verdict="NORMAL",
                    description=f"Observed travel time of {int(observed_delta_seconds)}s over {dist_km}km matches realistic traffic flow ({required_speed_kmh} km/h).",
                    severity_impact=0.0
                )
            )
            return (
                "NO_ANOMALY",
                "NONE",
                0.0,
                evidence_checklist,
                f"Sighting transition of '{plate_normalized}' between {source_camera_id} and {target_camera_id} is physically and topologically consistent."
            )

        elif graph_status == "TOO_SLOW":
            evidence_checklist.append(
                EvidenceItem(
                    category="TEMPORAL_EVIDENCE",
                    verdict="NORMAL",
                    description=f"Observed transit time ({int(observed_delta_seconds)}s) is slower than expected corridor travel. Likely caused by traffic congestion, stops, or parking.",
                    severity_impact=0.0
                )
            )
            return (
                "NO_ANOMALY",
                "LOW",
                0.10,
                evidence_checklist,
                f"Vehicle '{plate_normalized}' transit was delayed ({int(observed_delta_seconds)}s), consistent with standard urban congestion."
            )

        # 5. Visual Re-ID Cross-Check Evidence
        if reid_similarity is not None:
            if reid_similarity < 0.40:
                # Strong visual mismatch with matching plate -> Strongest cloning evidence!
                s_reid = 0.90
                evidence_checklist.append(
                    EvidenceItem(
                        category="VEHICLE_REID_EVIDENCE",
                        verdict="CONTRADICTORY",
                        description=f"Visual signature mismatch ({int(reid_similarity*100)}% Re-ID score). Vehicles exhibit completely different visual body attributes.",
                        severity_impact=0.40
                    )
                )
            elif reid_similarity >= 0.75:
                # Same visual vehicle
                s_reid = 0.0
                evidence_checklist.append(
                    EvidenceItem(
                        category="VEHICLE_REID_EVIDENCE",
                        verdict="CONSISTENT",
                        description=f"Visual signatures match ({int(reid_similarity*100)}% Re-ID similarity). Likely the exact same physical vehicle.",
                        severity_impact=0.10
                    )
                )
        else:
            evidence_checklist.append(
                EvidenceItem(
                    category="VEHICLE_REID_EVIDENCE",
                    verdict="INCONCLUSIVE",
                    description="Visual Re-ID signature unavailable for one or both camera sightings.",
                    severity_impact=0.0
                )
            )

        # 6. Composite Anomaly Score Formula
        # When kinematic impossibility is primary (s_kin > 0), base scale is 0.85
        base_anomaly = max(s_kin * 0.88, s_topo * 0.85)
        raw_score = base_anomaly + (0.12 * s_reid)
        # Scale by OCR confidence product
        anomaly_score = round(max(0.0, min(1.0, raw_score * ocr_prod)), 3)

        # 7. Alert Classification & Severity
        if graph_status == "TOO_FAST":
            alert_type = "POSSIBLE_CLONED_PLATE"
        elif graph_status == "NO_FEASIBLE_PATH":
            alert_type = "TOPOLOGY_INCONSISTENT"
        else:
            alert_type = "POSSIBLE_CLONED_PLATE"

        if anomaly_score >= 0.85:
            severity = "CRITICAL"
        elif anomaly_score >= 0.70:
            severity = "HIGH"
        elif anomaly_score >= 0.50:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        # 8. Human-Readable Explanation
        explanation = (
            f"ALERT: {alert_type.replace('_', ' ')} ({severity} severity, {int(anomaly_score*100)}% anomaly score). "
            f"License plate '{plate_normalized}' sighted at {source_camera_id} and {target_camera_id} separated by {dist_km} km "
            f"in only {int(observed_delta_seconds)}s (required average speed {required_speed_kmh} km/h vs {speed_limit_kmh} km/h limit). "
            f"Physically impossible transition across the directed road network."
        )

        return alert_type, severity, anomaly_score, evidence_checklist, explanation
