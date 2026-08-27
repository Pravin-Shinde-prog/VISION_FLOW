import random
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.models.camera import Camera
from app.models.road_edge import RoadEdge
from app.models.vehicle import Vehicle
from app.models.plate import VehiclePlate
from app.models.detection import Detection
from app.simulation.config import SimulationConfig
from app.simulation.vehicle_generator import VehicleGenerator, SyntheticVehicle
from app.simulation.route_generator import RouteGenerator
from app.simulation.event_generator import EventGenerator


class TrafficSimulator:
    """
    Core engine orchestrating synthetic traffic generation and PostgreSQL persistence.
    Produces normalized detection events over the existing directed camera network.
    """

    def __init__(self, config: Optional[SimulationConfig] = None):
        self.config = config or SimulationConfig()
        # Deterministic random generator
        self.rng = random.Random(self.config.seed)
        self.vehicle_generator = VehicleGenerator(self.rng)
        self.event_generator = EventGenerator(self.rng)

    async def run(self, db_session: Optional[AsyncSession] = None) -> Dict[str, Any]:
        """
        Executes a complete simulation run and commits generated vehicles, plates, and detections.
        """
        start_wall_time = time.perf_counter()

        if db_session:
            return await self._run_with_session(db_session, start_wall_time)
        else:
            async with async_session_factory() as session:
                return await self._run_with_session(session, start_wall_time)

    async def _run_with_session(self, session: AsyncSession, start_wall_time: float) -> Dict[str, Any]:
        # 1. Fetch existing camera network topology from DB
        cameras_query = await session.execute(select(Camera).order_by(Camera.id))
        cameras = list(cameras_query.scalars().all())

        edges_query = await session.execute(select(RoadEdge).order_by(RoadEdge.id))
        road_edges = list(edges_query.scalars().all())

        if not cameras:
            raise RuntimeError("Cannot run simulation: No cameras found in database. Seed cameras first.")

        # 2. Setup route generator
        route_gen = RouteGenerator(cameras, road_edges, self.rng)

        # 3. Generate synthetic fleet
        fleet = self.vehicle_generator.generate_fleet(self.config.vehicle_count, self.config)

        sim_start_time = self.config.get_start_time()
        sim_end_time = sim_start_time

        created_vehicles_count = 0
        created_plates_count = 0
        created_events_count = 0

        # 4. Process each vehicle and generate events
        for synthetic_v in fleet:
            # Generate route
            route = route_gen.generate_route(self.config.events_per_vehicle)
            if not route:
                continue

            # Generate chronological sightings
            raw_events = self.event_generator.generate_events(
                synthetic_v, route, sim_start_time, self.config
            )
            if not raw_events:
                continue

            first_seen = raw_events[0]["timestamp"]
            last_seen = raw_events[-1]["timestamp"]

            if last_seen > sim_end_time:
                sim_end_time = last_seen

            # 4a. Persist Vehicle Model
            vehicle_model = Vehicle(
                vehicle_uid=synthetic_v.vehicle_uid,
                vehicle_type=synthetic_v.vehicle_type,
                color=synthetic_v.color,
                make=synthetic_v.make,
                model=synthetic_v.model,
                window_tint=synthetic_v.window_tint,
                visual_features=synthetic_v.visual_features,
                first_seen_at=first_seen,
                last_seen_at=last_seen,
            )
            session.add(vehicle_model)
            await session.flush()
            created_vehicles_count += 1

            # 4b. Persist VehiclePlate Model (if readable)
            plate_model: Optional[VehiclePlate] = None
            if synthetic_v.normalized_plate:
                plate_model = VehiclePlate(
                    vehicle_id=vehicle_model.id,
                    normalized_plate=synthetic_v.normalized_plate,
                    raw_plate_text=synthetic_v.raw_plate_text,
                    state_code=synthetic_v.state_code,
                    confidence=synthetic_v.ocr_confidence,
                    status="valid" if synthetic_v.plate_state != "DAMAGED" else "anomaly",
                    anomaly_flags=synthetic_v.plate_anomaly_flags,
                    first_seen_at=first_seen,
                    last_seen_at=last_seen,
                )
                session.add(plate_model)
                await session.flush()
                created_plates_count += 1

            # 4c. Persist Detections
            for evt in raw_events:
                detection_model = Detection(
                    detection_uid=evt["detection_uid"],
                    camera_id=evt["camera_id"],
                    vehicle_id=vehicle_model.id,
                    plate_id=plate_model.id if plate_model else None,
                    timestamp=evt["timestamp"],
                    plate_number=evt["plate_number"],
                    ocr_confidence=evt["ocr_confidence"],
                    vehicle_color=evt["vehicle_color"],
                    vehicle_type=evt["vehicle_type"],
                    snapshot_path=evt["snapshot_path"],
                    direction_travel=evt["direction_travel"],
                    plate_anomaly_flags=evt["plate_anomaly_flags"],
                    processing_metadata=evt["processing_metadata"],
                    association_confidence=evt["association_confidence"],
                )
                session.add(detection_model)
                created_events_count += 1

        await session.commit()

        duration_sec = round(time.perf_counter() - start_wall_time, 3)

        return {
            "status": "completed",
            "vehicles_created": created_vehicles_count,
            "plates_created": created_plates_count,
            "events_created": created_events_count,
            "seed": self.config.seed,
            "start_time": sim_start_time,
            "end_time": sim_end_time,
            "duration_seconds": duration_sec,
            "message": f"Successfully simulated {created_vehicles_count} vehicles and {created_events_count} camera sightings."
        }
