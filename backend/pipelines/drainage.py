import networkx as nx
from typing import List, Tuple, Dict
from .dtm import DTMProcessor

class SewagePlanner:
    def __init__(self, dtm: DTMProcessor):
        self.dtm = dtm

    def plan_network(self, nodes: List[Tuple[float, float]], road_graph: nx.Graph) -> List[Dict]:
        """
        Find optimal path for sewage pipes along roads, preferring downward slope.
        """
        # nodes: [(lon1, lat1), (lon2, lat2), ...] - building centroids
        # road_graph: nx.Graph with nodes as (lon, lat) and edges representing roads
        
        # 1. Update road_graph edges with elevation-aware costs
        weighted_graph = nx.DiGraph()
        
        for u, v, data in road_graph.edges(data=True):
            slope = self.dtm.get_slope(u, v)
            dist = data.get('distance', 1.0)
            
            # Base cost is distance
            base_cost = dist
            
            # Gravity constraint: 
            # Prefer downward (negative slope)
            # High penalty for upward (positive slope)
            if slope > 0:
                cost_uv = base_cost * (1 + slope * 10) # Heavy penalty
                cost_vu = base_cost * (0.5) # Prefer downward
            else:
                cost_uv = base_cost * (0.5) # Prefer downward
                cost_vu = base_cost * (1 + abs(slope) * 10)
                
            weighted_graph.add_edge(u, v, weight=cost_uv)
            weighted_graph.add_edge(v, u, weight=cost_vu)

        # 2. Identify the lowest point as the 'sink' node
        # In production, this would be the treatment plant or a natural low point
        nodes_with_elevation = [(n, self.dtm.get_elevation(n[0], n[1])) for n in road_graph.nodes()]
        sink_node = min(nodes_with_elevation, key=lambda x: x[1])[0]

        # 3. Route each building to the nearest road node, then to the sink
        results = []
        for building_loc in nodes:
            # Find nearest road node
            nearest_road_node = min(road_graph.nodes(), 
                                  key=lambda n: (n[0]-building_loc[0])**2 + (n[1]-building_loc[1])**2)
            
            try:
                path = nx.shortest_path(weighted_graph, source=nearest_road_node, target=sink_node, weight='weight')
                results.append({
                    "building": building_loc,
                    "path": path,
                    "cost": sum(weighted_graph[u][v]['weight'] for u, v in zip(path, path[1:]))
                })
            except nx.NetworkXNoPath:
                continue
                
        return results

    def find_optimal_path(self, nodes: List[Tuple[float, float]], road_graph: nx.Graph) -> List[Dict]:
        return self.plan_network(nodes, road_graph)
