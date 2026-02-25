import numpy as np
import networkx as nx
from typing import List, Tuple, Dict
from sklearn.cluster import KMeans

class ElectricityPlanner:
    def __init__(self):
        pass

    def optimize_grid(self, buildings: List[Tuple[float, float]], max_kva_per_transformer: float = 100.0) -> Dict:
        """
        Cluster buildings into transformer zones and optimize LV line routing.
        """
        if not buildings: return {}
        
        # 1. K-Means Clustering on building coordinates
        # Simplified: Guess K based on total estimated load
        avg_kva_per_home = 3.0
        total_estimated_kva = len(buildings) * avg_kva_per_home
        n_clusters = int(np.ceil(total_estimated_kva / max_kva_per_transformer))
        
        coords = np.array(buildings)
        kmeans = KMeans(n_clusters=max(1, n_clusters), n_init=10)
        clusters = kmeans.fit_predict(coords)
        centroids = kmeans.cluster_centers_

        transformer_zones = []
        for i in range(len(centroids)):
            zone_buildings = [buildings[j] for j in range(len(buildings)) if clusters[j] == i]
            
            # 2. Minimum Spanning Tree for LV grid within the zone
            # Connect buildings to each other and to the transformer (centroid)
            nodes = zone_buildings + [tuple(centroids[i])]
            g = nx.Graph()
            for u_idx, u in enumerate(nodes):
                for v_idx, v in enumerate(nodes):
                    if u_idx < v_idx:
                        dist = np.sqrt((u[0]-v[0])**2 + (u[1]-v[1])**2)
                        g.add_edge(u, v, weight=dist)
            
            mst = nx.minimum_spanning_tree(g, weight='weight')
            
            transformer_zones.append({
                "transformer_loc": tuple(centroids[i]),
                "buildings_count": len(zone_buildings),
                "grid_edges": list(mst.edges())
            })

        return {
            "transformer_zones": transformer_zones,
            "total_clusters": n_clusters
        }
