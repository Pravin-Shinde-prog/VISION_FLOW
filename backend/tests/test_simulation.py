import pytest
import random
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.camera import Camera
from app.models.road_edge import RoadEdge
from app.simulation.config import SimulationConfig
from app.simulation.vehicle_generator import VehicleGenerator
from app.simulation.route_generator import RouteGenerator
from app.simulation.event_generator import EventGenerator
from app.simulation.engine import TrafficSimulator
from app.simulation.cleanup import cleanup_simulation_data


@pytest.mark.anyio
async def test_synthetic_vehicle_generation():
    """Verify fleet size, attribute validity, and plate readability states."""
    rng = random.Random(42)
    config = SimulationConfig(vehicle_count=50)
    generator = VehicleGenerator(rng)
    fleet = generator.generate_fleet(50, config)

    assert len(fleet) == 50
    uids = {v.vehicle_uid for v in fleet}
    assert len(uids) == 50

    plates = [v.normalized_plate for v in fleet if v.normalized_plate is not None]
    assert len(plates) == len(set(plates))

    for v in fleet:
        assert v.vehicle_type in ["SUV", "sedan", "hatchback", "motorcycle", "van", "truck"]
        assert len(v.color) > 0
        assert len(v.make) > 0
        assert len(v.model) > 0
        assert v.visual_features["simulation"] is True
        assert v.visual_features["data_source"] == "simulation"

        if v.plate_state == "OCCLUDED":
            assert v.normalized_plate is None
            assert v.ocr_confidence is None
        else:
            assert v.normalized_plate.startswith("MH12")
            assert 0.40 <= v.ocr_confidence <= 1.0


@pytest.mark.anyio
async def test_route_generation_follows_directed_graph(db_session: AsyncSession):
    """
    Verifies that every generated route strictly follows existing directed RoadEdge connections.
    """
    cams_res = await db_session.execute(select(Camera))
    cameras = list(cams_res.scalars().all())

    edges_res = await db_session.execute(select(RoadEdge))
    edges = list(edges_res.scalars().all())

    assert len(cameras) >= 15
    assert len(edges) >= 17

    valid_directed_edges = {(e.source_camera_id, e.destination_camera_id) for e in edges}

    rng = random.Random(42)
    route_gen = RouteGenerator(cameras, edges, rng)

    for _ in range(30):
        route = route_gen.generate_route(steps_count=5)
        assert len(route) >= 1

        for i in range(len(route) - 1):
            curr_cam_id = route[i].camera.id
            next_cam_id = route[i + 1].camera.id
            edge = route[i + 1].edge_from_prev

            assert (curr_cam_id, next_cam_id) in valid_directed_edges
            assert edge is not None
            assert edge.source_camera_id == curr_cam_id
            assert edge.destination_camera_id == next_cam_id


@pytest.mark.anyio
async def test_travel_time_physics_and_chronology(db_session: AsyncSession):
    """
    Verifies that generated timestamps are strictly monotonically increasing
    and travel times adhere to physical distance and road speed expectations.
    """
    cams_res = await db_session.execute(select(Camera))
    cameras = list(cams_res.scalars().all())
    edges_res = await db_session.execute(select(RoadEdge))
    edges = list(edges_res.scalars().all())

    rng = random.Random(42)
    config = SimulationConfig(vehicle_count=10, events_per_vehicle=5)
    veh_gen = VehicleGenerator(rng)
    route_gen = RouteGenerator(cameras, edges, rng)
    evt_gen = EventGenerator(rng)

    fleet = veh_gen.generate_fleet(10, config)
    base_time = datetime(2026, 8, 27, 10, 0, 0, tzinfo=timezone.utc)

    for v in fleet:
        route = route_gen.generate_route(5)
        events = evt_gen.generate_events(v, route, base_time, config)

        for i in range(len(events) - 1):
            t_curr = events[i]["timestamp"]
            t_next = events[i + 1]["timestamp"]

            assert t_next > t_curr

            elapsed_seconds = (t_next - t_curr).total_seconds()
            edge = route[i + 1].edge_from_prev
            assert elapsed_seconds >= edge.expected_min_travel_seconds * 0.85


@pytest.mark.anyio
async def test_seed_reproducibility():
    """Verify that using the same seed produces identical synthetic fleets."""
    config1 = SimulationConfig(vehicle_count=20, seed=999)
    config2 = SimulationConfig(vehicle_count=20, seed=999)

    fleet1 = VehicleGenerator(random.Random(config1.seed)).generate_fleet(20, config1)
    fleet2 = VehicleGenerator(random.Random(config2.seed)).generate_fleet(20, config2)

    for v1, v2 in zip(fleet1, fleet2):
        assert v1.vehicle_uid == v2.vehicle_uid
        assert v1.normalized_plate == v2.normalized_plate
        assert v1.color == v2.color
        assert v1.make == v2.make
        assert v1.model == v2.model
        assert v1.ocr_confidence == v2.ocr_confidence
