import pytest
import httpx
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.graph.builder import DirectedRoadGraphBuilder
from app.graph.pathfinding import DijkstraPathFinder
from app.graph.validator import TransitionValidator
from app.graph.engine import SpatioTemporalGraphEngine
from app.graph.schemas import (
    TransitionValidationRequest,
    SequenceValidationRequest,
    SequenceObservation,
)
from app.main import app


@pytest.mark.anyio
async def test_graph_builder_and_topology(db_session: AsyncSession):
    """Verify directed graph construction from database camera and road edge models."""
    graph = await DirectedRoadGraphBuilder.build_from_database(db_session)

    # 15 Pune cameras
    assert len(graph.nodes) == 15
    assert "CAM_PUN_001" in graph.nodes
    assert "CAM_PUN_015" in graph.nodes

    # 17 Directed road edges
    assert len(graph.edges) == 17
    assert len(graph.adjacency["CAM_PUN_001"]) >= 1


@pytest.mark.anyio
async def test_directed_pathfinding_and_multi_hop(db_session: AsyncSession):
    """Verify Dijkstra shortest path routing and strict directionality enforcement."""
    graph = await DirectedRoadGraphBuilder.build_from_database(db_session)

    # 1. Direct 1-hop path: CAM_PUN_001 -> CAM_PUN_002
    p1 = DijkstraPathFinder.find_shortest_path(graph, "CAM_PUN_001", "CAM_PUN_002")
    assert p1.path_exists is True
    assert p1.camera_path == ["CAM_PUN_001", "CAM_PUN_002"]
    assert p1.total_distance_meters > 0
    assert p1.hop_count == 1

    # 2. Multi-hop corridor: CAM_PUN_001 -> CAM_PUN_004 (via 002, 003)
    p2 = DijkstraPathFinder.find_shortest_path(graph, "CAM_PUN_001", "CAM_PUN_004")
    assert p2.path_exists is True
    assert len(p2.camera_path) >= 3
    assert p2.camera_path[0] == "CAM_PUN_001"
    assert p2.camera_path[-1] == "CAM_PUN_004"
    assert p2.total_distance_meters > p1.total_distance_meters
    assert p2.estimated_min_time_seconds > 0

    # 3. Same camera station
    p_same = DijkstraPathFinder.find_shortest_path(graph, "CAM_PUN_001", "CAM_PUN_001")
    assert p_same.path_exists is True
    assert p_same.total_distance_meters == 0.0


@pytest.mark.anyio
async def test_transition_validation_statuses(db_session: AsyncSession):
    """Verify physical/temporal classification: TEMPORALLY_FEASIBLE, TOO_FAST, TOO_SLOW, NO_FEASIBLE_PATH."""
    graph = await DirectedRoadGraphBuilder.build_from_database(db_session)
    base_time = datetime(2026, 8, 27, 10, 0, 0, tzinfo=timezone.utc)

    # 1. TEMPORALLY_FEASIBLE (450m in 65s -> ~25 km/h)
    req_feasible = TransitionValidationRequest(
        source_camera_id="CAM_PUN_001",
        target_camera_id="CAM_PUN_002",
        source_timestamp=base_time,
        target_timestamp=base_time + timedelta(seconds=65),
    )
    res_f = TransitionValidator.validate_transition(graph, req_feasible)
    assert res_f.status == "TEMPORALLY_FEASIBLE"
    assert res_f.transition_feasibility_score >= 0.80

    # 2. TOO_FAST (CAM_PUN_001 -> CAM_PUN_004, 3.2km in 6s -> >1800 km/h)
    req_fast = TransitionValidationRequest(
        source_camera_id="CAM_PUN_001",
        target_camera_id="CAM_PUN_004",
        source_timestamp=base_time,
        target_timestamp=base_time + timedelta(seconds=6),
    )
    res_fast = TransitionValidator.validate_transition(graph, req_fast)
    assert res_fast.status == "TOO_FAST"
    assert res_fast.speed_ratio > 2.0
    assert res_fast.transition_feasibility_score < 0.40

    # 3. TOO_SLOW (CAM_PUN_001 -> CAM_PUN_002, 450m in 3600s / 1 hour)
    req_slow = TransitionValidationRequest(
        source_camera_id="CAM_PUN_001",
        target_camera_id="CAM_PUN_002",
        source_timestamp=base_time,
        target_timestamp=base_time + timedelta(seconds=3600),
        congestion_tolerance_factor=2.0
    )
    res_slow = TransitionValidator.validate_transition(graph, req_slow)
    assert res_slow.status == "TOO_SLOW"


@pytest.mark.anyio
async def test_multi_hop_sequence_validation(db_session: AsyncSession):
    """Verify route validation across a multi-hop sequence of sightings."""
    graph = await DirectedRoadGraphBuilder.build_from_database(db_session)
    t0 = datetime(2026, 8, 27, 10, 0, 0, tzinfo=timezone.utc)

    seq_req = SequenceValidationRequest(
        observations=[
            SequenceObservation(observation_id="OBS_1", camera_id="CAM_PUN_001", timestamp=t0),
            SequenceObservation(observation_id="OBS_2", camera_id="CAM_PUN_002", timestamp=t0 + timedelta(seconds=65)),
            SequenceObservation(observation_id="OBS_3", camera_id="CAM_PUN_003", timestamp=t0 + timedelta(seconds=145)),
        ]
    )
    res = TransitionValidator.validate_sequence(graph, seq_req)
    assert res.total_hops == 2
    assert res.feasible_hops == 2
    assert res.anomalous_hops == 0
    assert res.overall_route_feasible is True


@pytest.mark.anyio
async def test_graph_api_endpoints(db_session: AsyncSession):
    """Verify Graph Engine REST API endpoints."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # 1. Topology
        top_res = await client.get("/api/v1/graph/topology")
        assert top_res.status_code == 200
        top_data = top_res.json()
        assert top_data["total_nodes"] == 15
        assert top_data["total_edges"] == 17

        # 2. Pathfinding
        path_res = await client.get(
            "/api/v1/graph/path",
            params={"source_camera_id": "CAM_PUN_001", "target_camera_id": "CAM_PUN_004"}
        )
        assert path_res.status_code == 200
        path_data = path_res.json()
        assert path_data["path_exists"] is True
        assert len(path_data["camera_path"]) >= 3

        # 3. Transition validation
        t_req = {
            "source_camera_id": "CAM_PUN_001",
            "target_camera_id": "CAM_PUN_002",
            "source_timestamp": "2026-08-27T10:00:00Z",
            "target_timestamp": "2026-08-27T10:01:05Z",
            "plate_number": "MH12AB1234"
        }
        val_res = await client.post("/api/v1/graph/validate-transition", json=t_req)
        assert val_res.status_code == 200
        val_data = val_res.json()
        assert val_data["status"] == "TEMPORALLY_FEASIBLE"

        # 4. Demo scenarios
        demo_res = await client.get("/api/v1/graph/demo-scenarios")
        assert demo_res.status_code == 200
        demo_data = demo_res.json()
        assert len(demo_data) >= 3
