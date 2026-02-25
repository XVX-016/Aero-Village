from typing import List, Dict, Any
import numpy as np

class ProcurementEngine:
    # Standard Government Rates (Mock)
    RATES = {
        "sewage_pipe": 120,    # USD per meter
        "electrical_cable": 85, # USD per meter
        "transformer_unit": 15000, 
        "manhole_unit": 800,
        "base_labor_rate": 45  # USD per hour
    }

    def __init__(self, dtm_processor=None):
        self.dtm = dtm_processor

    def estimate_project_cost(self, infra_type: str, segments: List[List[List[float]]], metadata: Dict = None) -> Dict[str, Any]:
        """
        Calculate budgetary requirements for a given infrastructure layout.
        Costs are adjusted based on distance and terrain difficulty.
        """
        total_length_m = 0
        for seg in segments:
            # Simple Euclidean distance for mock (scale to approx meters)
            dist = np.sqrt((seg[1][0] - seg[0][0])**2 + (seg[1][1] - seg[0][1])**2) * 111320 
            total_length_m += dist

        # Complexity multiplier should be deterministic for identical inputs.
        complexity_factor = 1.0
        if metadata and "complexity_factor" in metadata:
            complexity_factor = float(metadata["complexity_factor"])

        material_rate = self.RATES.get(f"{infra_type}_pipe", self.RATES.get(f"{infra_type}_cable", 100))
        
        material_cost = total_length_m * material_rate
        labor_cost = (total_length_m / 5) * self.RATES["base_labor_rate"] * complexity_factor # 1hr per 5m
        
        capec_total = material_cost + labor_cost
        contingency = capec_total * 0.15 # 15% safety buffer
        
        return {
            "project_type": infra_type,
            "total_length_m": round(total_length_m, 2),
            "complexity_factor": complexity_factor,
            "breakdown": {
                "materials": round(material_cost, 2),
                "labor": round(labor_cost, 2),
                "contingency": round(contingency, 2)
            },
            "total_estimate": round(capec_total + contingency, 2),
            "currency": "USD",
            "confidence_score": 0.7 if complexity_factor > 1.0 else 0.85
        }

    def generate_dossier_data(self, project_summary: Dict, compliance_data: Dict) -> Dict:
        """Structure data for formal government report generation."""
        return {
            "header": {
                "authority": "Ministry of Rural Development",
                "department": "Infrastructure Planning Division",
                "timestamp": "2026-02-21T19:30:00Z"
            },
            "project": project_summary,
            "compliance": compliance_data,
            "approval_status": "PROVISIONAL" if compliance_data.get("score", 0) > 0.8 else "REJECTED"
        }
