import heapq
from typing import Dict, List, Optional, Tuple
from app.graph.builder import DirectedRoadGraph
from app.graph.schemas import GraphPathResponse


class DijkstraPathFinder:
    """
    Implements Dijkstra's algorithm for directed shortest weighted path on road graph G=(V,E).
    Weight metric: physical road distance in meters.
    Strictly enforces edge directionality (A->B does NOT permit B->A).
    """

    @classmethod
    def find_shortest_path(
        cls,
        graph: DirectedRoadGraph,
        source_camera_id: str,
        target_camera_id: str
    ) -> GraphPathResponse:
        src = source_camera_id.strip().upper()
        dst = target_camera_id.strip().upper()

        if src not in graph.nodes or dst not in graph.nodes:
            return GraphPathResponse(
                path_exists=False,
                source_camera_id=src,
                target_camera_id=dst,
                camera_path=[],
                node_names_path=[],
                edge_ids=[],
                total_distance_meters=0.0,
                estimated_min_time_seconds=0.0,
                estimated_max_time_seconds=0.0,
                effective_speed_limit_kmh=0.0,
                hop_count=0,
                explanation=f"One or both cameras ('{src}', '{dst}') do not exist in the active road network."
            )

        # Same camera / zero distance
        if src == dst:
            node = graph.get_node(src)
            return GraphPathResponse(
                path_exists=True,
                source_camera_id=src,
                target_camera_id=dst,
                camera_path=[src],
                node_names_path=[node.name if node else src],
                edge_ids=[],
                total_distance_meters=0.0,
                estimated_min_time_seconds=0.0,
                estimated_max_time_seconds=0.0,
                effective_speed_limit_kmh=50.0,
                hop_count=0,
                explanation="Source and destination are identical (zero distance stationary location)."
            )

        # Dijkstra priority queue: (accumulated_dist, current_node, path_nodes, path_edges)
        pq: List[Tuple[float, str, List[str], List[int]]] = [(0.0, src, [src], [])]
        visited: Dict[str, float] = {}

        while pq:
            curr_dist, curr_node, node_path, edge_path = heapq.heappop(pq)

            if curr_node in visited and visited[curr_node] <= curr_dist:
                continue
            visited[curr_node] = curr_dist

            if curr_node == dst:
                # Destination reached! Reconstruct accumulated metrics
                tot_dist = 0.0
                min_sec = 0.0
                max_sec = 0.0
                speed_limits = []
                node_names = []

                for nid in node_path:
                    n = graph.get_node(nid)
                    node_names.append(n.name if n else nid)

                for eid in edge_path:
                    edge = graph.get_edge(eid)
                    if edge:
                        tot_dist += edge.distance_meters
                        min_sec += edge.expected_min_travel_seconds
                        max_sec += edge.expected_max_travel_seconds
                        speed_limits.append(edge.speed_limit_kmh)

                eff_speed_limit = round(sum(speed_limits) / float(len(speed_limits)), 1) if speed_limits else 50.0

                return GraphPathResponse(
                    path_exists=True,
                    source_camera_id=src,
                    target_camera_id=dst,
                    camera_path=node_path,
                    node_names_path=node_names,
                    edge_ids=edge_path,
                    total_distance_meters=round(tot_dist, 1),
                    estimated_min_time_seconds=round(min_sec, 1),
                    estimated_max_time_seconds=round(max_sec, 1),
                    effective_speed_limit_kmh=eff_speed_limit,
                    hop_count=len(edge_path),
                    explanation=f"Directed feasible path found traversing {len(node_path)} cameras ({round(tot_dist/1000.0, 2)} km)."
                )

                # Explore directed outgoing neighbors
            for neighbor_code, eid in graph.adjacency.get(curr_node, []):
                edge = graph.get_edge(eid)
                if not edge:
                    continue
                new_dist = curr_dist + edge.distance_meters
                if neighbor_code not in visited or new_dist < visited[neighbor_code]:
                    heapq.heappush(
                        pq,
                        (new_dist, neighbor_code, node_path + [neighbor_code], edge_path + [eid])
                    )

        # No path found in directed graph
        return GraphPathResponse(
            path_exists=False,
            source_camera_id=src,
            target_camera_id=dst,
            camera_path=[],
            node_names_path=[],
            edge_ids=[],
            total_distance_meters=0.0,
            estimated_min_time_seconds=0.0,
            estimated_max_time_seconds=0.0,
            effective_speed_limit_kmh=0.0,
            hop_count=0,
            explanation=f"NO_FEASIBLE_PATH: No directed road connection exists from '{src}' to '{dst}' in the Pune road network."
        )
