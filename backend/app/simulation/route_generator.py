import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from app.models.camera import Camera
from app.models.road_edge import RoadEdge


@dataclass
class RouteStep:
    camera: Camera
    edge_from_prev: Optional[RoadEdge]  # None for initial starting camera


class RouteGenerator:
    """
    Generates topological vehicle trajectories strictly following the directed road graph.
    Prevents teleportation or unconnected node transitions.
    """

    def __init__(self, cameras: List[Camera], road_edges: List[RoadEdge], rng: random.Random):
        self.cameras = cameras
        self.road_edges = road_edges
        self.rng = rng

        self.cam_by_id: Dict[int, Camera] = {c.id: c for c in cameras}

        # Build directed adjacency list: source_camera_id -> List[RoadEdge]
        self.adj_list: Dict[int, List[RoadEdge]] = {c.id: [] for c in cameras}
        for edge in road_edges:
            if edge.is_active and edge.source_camera_id in self.adj_list:
                self.adj_list[edge.source_camera_id].append(edge)

        # Filter cameras that have at least one outgoing edge as candidate start nodes
        self.start_candidates = [c for c in cameras if len(self.adj_list.get(c.id, [])) > 0]
        if not self.start_candidates:
            self.start_candidates = cameras

    def generate_route(self, steps_count: int) -> List[RouteStep]:
        """
        Generates a valid path of consecutive cameras following directed edges.
        """
        if not self.cameras:
            return []

        # Choose start node
        start_cam = self.rng.choice(self.start_candidates)
        route: List[RouteStep] = [RouteStep(camera=start_cam, edge_from_prev=None)]

        current_cam = start_cam
        for _ in range(steps_count - 1):
            outgoing_edges = self.adj_list.get(current_cam.id, [])
            if not outgoing_edges:
                # Dead end reached; stop route or restart from another candidate
                break

            chosen_edge = self.rng.choice(outgoing_edges)
            next_cam = self.cam_by_id.get(chosen_edge.destination_camera_id)
            if not next_cam:
                break

            route.append(RouteStep(camera=next_cam, edge_from_prev=chosen_edge))
            current_cam = next_cam

        return route
