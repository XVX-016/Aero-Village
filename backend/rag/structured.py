import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from models import ExtractedFeature, InfrastructureLayer


def _latest_ingestion_version(db: Session, project_id: str) -> Optional[int]:
    row = (
        db.query(ExtractedFeature.ingestion_version)
        .filter(ExtractedFeature.project_id == project_id)
        .order_by(ExtractedFeature.ingestion_version.desc())
        .first()
    )
    if not row:
        return None
    return int(row[0] or 1)


def get_building_summary(db: Session, project_id: str) -> Dict[str, Any]:
    latest = _latest_ingestion_version(db, project_id)
    if latest is None:
        return {
            "project_id": project_id,
            "feature_count": 0,
            "total_area_sq_m": 0.0,
            "average_area_sq_m": 0.0,
            "latest_ingestion_version": None,
        }

    rows = (
        db.query(ExtractedFeature)
        .filter(
            ExtractedFeature.project_id == project_id,
            ExtractedFeature.ingestion_version == latest,
            ExtractedFeature.type == "building",
        )
        .all()
    )
    total_area = sum(float(r.area_sq_m or 0.0) for r in rows)
    count = len(rows)
    return {
        "project_id": project_id,
        "feature_count": count,
        "total_area_sq_m": total_area,
        "average_area_sq_m": (total_area / count) if count else 0.0,
        "latest_ingestion_version": latest,
    }


def get_planning_summary(db: Session, project_id: str) -> Dict[str, Any]:
    rows = db.query(InfrastructureLayer).filter(InfrastructureLayer.project_id == project_id).all()
    by_type: Dict[str, int] = {}
    cost_totals: Dict[str, float] = {}
    for row in rows:
        infra_type = row.type or "unknown"
        by_type[infra_type] = by_type.get(infra_type, 0) + 1
        cost_totals[infra_type] = cost_totals.get(infra_type, 0.0) + float(row.cost_estimate or 0.0)
    return {
        "project_id": project_id,
        "segment_count": len(rows),
        "segments_by_type": by_type,
        "cost_totals_by_type": cost_totals,
    }


def estimate_transformer_count(building_count: int, max_kva_per_transformer: float = 100.0) -> int:
    if building_count <= 0:
        return 0
    avg_kva_per_home = 3.0
    total_estimated_kva = building_count * avg_kva_per_home
    return max(1, int((total_estimated_kva + max_kva_per_transformer - 1) // max_kva_per_transformer))


def load_ingestion_manifest(base_dir: Path, project_id: str) -> Dict[str, Any]:
    manifest_path = base_dir / "outputs" / "projects" / project_id / "artifacts" / "ingestion.json"
    if not manifest_path.exists():
        return {"exists": False, "path": str(manifest_path)}
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return {"exists": True, "path": str(manifest_path), "error": "manifest parse failed"}
    return {"exists": True, "path": str(manifest_path), "manifest": payload}


def build_structured_context(db: Session, base_dir: Path, project_id: str) -> Dict[str, Any]:
    building = get_building_summary(db, project_id)
    planning = get_planning_summary(db, project_id)
    manifest = load_ingestion_manifest(base_dir=base_dir, project_id=project_id)
    transformer_estimate = estimate_transformer_count(int(building.get("feature_count", 0)))
    return {
        "building_summary": building,
        "planning_summary": planning,
        "ingestion_manifest": manifest,
        "transformer_estimate": {
            "count": transformer_estimate,
            "method": "derived_from_building_count",
            "assumptions": {"avg_kva_per_home": 3.0, "max_kva_per_transformer": 100.0},
        },
    }


def infrastructure_gaps_summary(structured: Dict[str, Any]) -> Dict[str, Any]:
    planning = structured.get("planning_summary", {})
    by_type = planning.get("segments_by_type", {}) or {}
    gaps: List[str] = []
    for t in ["sewage", "electricity"]:
        if by_type.get(t, 0) == 0:
            gaps.append(f"No persisted {t} planning segments found.")
    if not structured.get("building_summary", {}).get("feature_count", 0):
        gaps.append("No ingested building features found.")
    if not gaps:
        gaps.append("No obvious data-level gaps detected in persisted records.")
    return {"gaps": gaps}

