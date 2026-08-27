import random
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from app.simulation.vehicle_generator import SyntheticVehicle
from app.simulation.route_generator import RouteStep


class EventGenerator:
    """
    Produces normalized detection observations from a synthetic vehicle traveling its route.
    Computes physically plausible timestamps using road edge travel distances and speed limits.
    """

    def __init__(self, rng: random.Random):
        self.rng = rng

    def generate_events(
        self,
        vehicle: SyntheticVehicle,
        route: List[RouteStep],
        base_start_time: datetime,
        config
    ) -> List[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []
        if not route:
            return events

        # Initial camera timestamp with slight offset (0 - 300s)
        current_time = base_start_time + timedelta(seconds=self.rng.uniform(0, 300))

        for idx, step in enumerate(route):
            cam = step.camera
            edge = step.edge_from_prev

            if edge is not None:
                # Compute travel time based on distance & speed limit with Gaussian variation
                min_sec = edge.expected_min_travel_seconds
                max_sec = edge.expected_max_travel_seconds or (min_sec * 3.0)

                # Base travel time between min and average
                base_travel = (min_sec + max_sec) / 2.0
                speed_fluctuation = self.rng.uniform(-config.speed_variation_pct, config.speed_variation_pct)
                travel_seconds = max(min_sec * 0.9, base_travel * (1.0 + speed_fluctuation))

                # Occasional traffic / intersection delay
                if self.rng.random() < config.delay_probability:
                    delay = self.rng.uniform(config.min_delay_seconds, config.max_delay_seconds)
                    travel_seconds += delay

                current_time += timedelta(seconds=travel_seconds)

            # Generate unique deterministic detection UID
            hex_suffix = "".join(self.rng.choices("0123456789abcdef", k=6))
            detection_uid = f"evt_sim_{self.rng.randint(100000, 999999)}_{hex_suffix}"
            snapshot_path = f"simulated://camera/{cam.camera_id}/event/{detection_uid}.jpg"

            # Normalized edge processing metadata
            edge_latency = round(self.rng.uniform(18.0, 38.0), 2)
            direction_travel = edge.direction if edge else "Inbound"

            # Bounding box coords [x1, y1, x2, y2]
            bbox = [
                self.rng.randint(100, 250),
                self.rng.randint(150, 300),
                self.rng.randint(600, 800),
                self.rng.randint(550, 750),
            ]

            processing_metadata = {
                "simulation": True,
                "data_source": "simulation",
                "city": "Pune",
                "edge_device_id": f"EDGE_JETSON_{cam.camera_id}",
                "edge_latency_ms": edge_latency,
                "bbox": bbox,
                "fps": 30.0,
                "model_version": "edge_sim_v1.0",
                "route_sequence_step": idx + 1,
            }

            events.append({
                "detection_uid": detection_uid,
                "camera_id": cam.id,
                "camera_code": cam.camera_id,
                "camera_name": cam.name,
                "timestamp": current_time,
                "plate_number": vehicle.normalized_plate,
                "ocr_confidence": vehicle.ocr_confidence,
                "vehicle_color": vehicle.color,
                "vehicle_type": vehicle.vehicle_type,
                "direction_travel": direction_travel,
                "snapshot_path": snapshot_path,
                "plate_anomaly_flags": vehicle.plate_anomaly_flags,
                "processing_metadata": processing_metadata,
                "association_confidence": round(self.rng.uniform(0.92, 0.99), 3),
            })

        return events
