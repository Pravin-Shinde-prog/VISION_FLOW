import time
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.graph.builder import DirectedRoadGraph, DirectedRoadGraphBuilder
from app.graph.pathfinding import DijkstraPathFinder
from app.graph.validator import TransitionValidator
from app.graph.demo_scenarios import GraphDemoScenarios
from app.graph.schemas import (
    GraphTopologyResponse,
    GraphPathResponse,
    TransitionValidationRequest,
    TransitionValidationResponse,
    SequenceValidationRequest,
    SequenceValidationResponse,
    GraphDemoScenario,
)


class SpatioTemporalGraphEngine:
    """
    Spatio-Temporal Graph Engine.
    Coordinates graph loading from DB, directed shortest-path routing,
    transition kinematics validation, and multi-camera route sequence verification.
    """

    _cached_graph: Optional[DirectedRoadGraph] = None
    _last_build_time: float = 0.0

    @classmethod
    async def get_graph(cls, db: AsyncSession, force_reload: bool = False) -> DirectedRoadGraph:
        # Cache graph in-memory for 60 seconds unless explicitly refreshed
        now = time.time()
        if cls._cached_graph is None or force_reload or (now - cls._last_build_time) > 60.0:
            cls._cached_graph = await DirectedRoadGraphBuilder.build_from_database(db)
            cls._last_build_time = now
        return cls._cached_graph

    @classmethod
    async def get_topology(cls, db: AsyncSession) -> GraphTopologyResponse:
        graph = await cls.get_graph(db)
        return graph.to_topology_response()

    @classmethod
    async def find_path(
        cls,
        source_camera_id: str,
        target_camera_id: str,
        db: AsyncSession
    ) -> GraphPathResponse:
        graph = await cls.get_graph(db)
        return DijkstraPathFinder.find_shortest_path(graph, source_camera_id, target_camera_id)

    @classmethod
    async def validate_transition(
        cls,
        req: TransitionValidationRequest,
        db: AsyncSession
    ) -> TransitionValidationResponse:
        graph = await cls.get_graph(db)
        return TransitionValidator.validate_transition(graph, req)

    @classmethod
    async def validate_sequence(
        cls,
        req: SequenceValidationRequest,
        db: AsyncSession
    ) -> SequenceValidationResponse:
        graph = await cls.get_graph(db)
        return TransitionValidator.validate_sequence(graph, req)

    @classmethod
    async def get_demo_scenarios(cls, db: AsyncSession) -> List[GraphDemoScenario]:
        graph = await cls.get_graph(db)
        return GraphDemoScenarios.get_scenarios(graph)
