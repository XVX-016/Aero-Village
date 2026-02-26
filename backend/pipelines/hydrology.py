import numpy as np
from typing import List, Dict, Any
from .dtm import DTMProcessor

class HydrologySimulator:
    def __init__(self, dtm: DTMProcessor):
        self.dtm = dtm

    def simulate_flood(self, bounds: List[float], rainfall_mm: float) -> Dict[str, Any]:
        """
        Simulate water accumulation based on rainfall and terrain.
        Simple Bathtub Model: Water accumulates in local depressions.
        """
        # bounds: [min_lon, min_lat, max_lon, max_lat]
        # In production: Use a grid-based D4/D8 flow accumulation algorithm.
        
        # Mock accumulation points for demonstration
        # We sample points within bounds and keep those with lower elevation
        min_lon, min_lat, max_lon, max_lat = bounds
        
        lons = np.linspace(min_lon, max_lon, 10)
        lats = np.linspace(min_lat, max_lat, 10)
        
        accumulation_zones = []
        
        # Get baseline elevation (center)
        center_elev = self.dtm.get_elevation((min_lon + max_lon)/2, (min_lat + max_lat)/2)
        
        for lon in lons:
            for lat in lats:
                elev = self.dtm.get_elevation(lon, lat)
                
                # If elevation is lower than center (depression) and rainfall is high
                if elev < center_elev and rainfall_mm > 50:
                    depth = (center_elev - elev) * (rainfall_mm / 100.0)
                    accumulation_zones.append({
                        "center": [lon, lat],
                        "depth_m": round(depth, 2),
                        "radius_m": depth * 50 # Spread based on depth
                    })
                    
        return {
            "rainfall_intensity": rainfall_mm,
            "accumulation_count": len(accumulation_zones),
            "zones": accumulation_zones,
            "risk_level": "High" if rainfall_mm > 100 else "Moderate" if rainfall_mm > 50 else "Low"
        }

    def assess_infrastructure_risk(self, infra_segments: List[Dict], flood_zones: List[Dict]) -> Dict:
        """Calculate percentage of infrastructure susceptible to flooding."""
        at_risk_count = 0
        total_count = len(infra_segments)
        
        if total_count == 0: return {"resilience_score": 100}
        
        for segment in infra_segments:
            start = segment.get("start")
            end = segment.get("end")
            if not start or not end:
                continue
            sx, sy = start
            ex, ey = end
            mx, my = (sx + ex) / 2, (sy + ey) / 2
            for zone in flood_zones:
                zx, zy = zone.get("center", [None, None])
                radius_m = float(zone.get("radius_m", 0.0))
                if zx is None or zy is None:
                    continue
                dx = (mx - zx) * 111_320
                dy = (my - zy) * 111_320
                if (dx * dx + dy * dy) <= (radius_m * radius_m):
                    at_risk_count += 1
                    break
            
        resilience = ((total_count - at_risk_count) / total_count) * 100
        return {
            "at_risk_count": at_risk_count,
            "resilience_score": round(resilience, 1)
        }
