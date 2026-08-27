from typing import Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import aliased

from app.models.camera import Camera
from app.models.road_edge import RoadEdge
from app.graph.schemas import GraphNode, GraphEdge, GraphTopologyResponse


class DirectedRoadGraph:
    """
    In-memory representation of the directed road graph G = (V, E).
    Nodes represent camera stations; edges represent directed road connections.
    """

    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: Dict[int, GraphEdge] = {}
        # Adjacency list: source_camera_id -> List[Tuple[destination_camera_id, edge_id]]
        self.adjacency: Dict[str, List[Tuple[str, int]]] = {}

    def add_node(self, node: GraphNode):
        self.nodes[node.camera_id] = node
        if node.camera_id not in self.adjacency:
            self.adjacency[node.camera_id] = []

    def add_edge(self, edge: GraphEdge):
        self.edges[edge.edge_id] = edge
        if edge.source_camera_id not in self.adjacency:
            self.adjacency[edge.source_camera_id] = []
        self.adjacency[edge.source_camera_id].append((edge.destination_camera_id, edge.edge_id))

    def get_node(self, camera_id: str) -> Optional[GraphNode]:
        return self.nodes.get(camera_id.upper())

    def get_edge(self, edge_id: int) -> Optional[GraphEdge]:
        return self.edges.get(edge_id)

    def to_topology_response(self) -> GraphTopologyResponse:
        return GraphTopologyResponse(
            total_nodes=len(self.nodes),
            total_edges=len(self.edges),
            nodes=list(self.nodes.values()),
            edges=list(self.edges.values()),
        )


class DirectedRoadGraphBuilder:
    """
    Constructs the directed road graph G = (V, E) dynamically from existing database records.
    """

    @classmethod
    async def build_from_database(cls, db: AsyncSession) -> DirectedRoadGraph:
        graph = DirectedRoadGraph()

        # 1. Fetch all cameras
        cam_query = select(Camera).order_by(Camera.camera_id)
        cam_res = await db.execute(cam_query)
        cameras = cam_res.scalars().all()

        cam_id_to_code: Dict[int, str] = {}

        for cam in cameras:
            cam_id_to_code[cam.id] = cam.camera_id
            graph.add_node(
                GraphNode(
                    camera_id=cam.camera_id,
                    name=cam.name,
                    latitude=cam.latitude,
                    longitude=cam.longitude,
                    sector=cam.sector,
                    road_name=cam.road_name,
                    is_active=cam.status in ("active", "warning", "online"),
                )
            )

        # 2. Fetch all directed road edges
        src_alias = aliased(Camera, name="src_cam")
        dst_alias = aliased(Camera, name="dst_cam")

        edge_query = (
            select(
                RoadEdge,
                src_alias.camera_id.label("src_code"),
                dst_alias.camera_id.label("dst_code"),
            )
            .join(src_alias, RoadEdge.source_camera_id == src_alias.id)
            .join(dst_alias, RoadEdge.destination_camera_id == dst_alias.id)
            .where(RoadEdge.is_active.is_(True))
            .order_by(RoadEdge.id)
        )

        edge_res = await db.execute(edge_query)
        rows = edge_res.all()

        for edge, src_code, dst_code in rows:
            min_sec = edge.expected_min_travel_seconds
            max_sec = edge.expected_max_travel_seconds or (min_sec * 3.5)
            spd_lim = edge.speed_limit_kmh or 50.0

            graph.add_edge(
                GraphEdge(
                    edge_id=edge.id,
                    source_camera_id=src_code,
                    destination_camera_id=dst_code,
                    distance_meters=edge.distance_meters,
                    speed_limit_kmh=spd_lim,
                    expected_min_travel_seconds=min_sec,
                    expected_max_travel_seconds=max_sec,
                    road_name=edge.road_name,
                    direction=edge.direction,
                )
            )

        return graph
