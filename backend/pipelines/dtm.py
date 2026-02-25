import rasterio
import numpy as np
from typing import Tuple, Optional

class DTMProcessor:
    def __init__(self, dtm_path: Optional[str] = None):
        self.dtm_path = dtm_path
        self.src = None
        if dtm_path:
            self.src = rasterio.open(dtm_path)

    def get_elevation(self, lon: float, lat: float) -> float:
        """Get elevation at specific coordinates"""
        if not self.src:
            # Mock elevation if no DTM is provided (slight gradient for testing)
            return 100.0 + (lat * 10.0) + (lon * 5.0)
            
        try:
            # Sample the raster at the given lon/lat
            # Coordinates must be in the raster's CRS
            vals = list(self.src.sample([(lon, lat)]))
            return float(vals[0][0])
        except Exception as e:
            print(f"Elevation lookup failed: {e}")
            return 100.0

    def get_slope(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Calculate slope percentage between two points"""
        z1 = self.get_elevation(p1[0], p1[1])
        z2 = self.get_elevation(p2[0], p2[1])
        
        # Approximate distance in meters (very rough for short distances)
        # 1 deg ~ 111km
        dx = (p2[0] - p1[0]) * 111000
        dy = (p2[1] - p1[1]) * 111000
        dist = np.sqrt(dx**2 + dy**2)
        
        if dist == 0: return 0.0
        return ((z2 - z1) / dist) * 100

    def close(self):
        if self.src:
            self.src.close()
