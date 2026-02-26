import json
import hashlib
import logging
import sys
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import geopandas as gpd
import rasterio
from fastapi import BackgroundTasks, Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from geoalchemy2 import WKTElement
from geoalchemy2.shape import to_shape
from shapely.geometry import LineString
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import SessionLocal, get_db, init_db
from models import ExtractedFeature, InfrastructureLayer, ProjectRun
from pipelines.drainage import SewagePlanner
from pipelines.dtm import DTMProcessor
from pipelines.electricity import ElectricityPlanner
from pipelines.hydrology import HydrologySimulator
from pipelines.procurement import ProcurementEngine
from rag.service import HybridRAGService

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("aerovillage.api")

app = FastAPI(
    title="Aerovillage Smart Village Intelligence Platform",
    description="Backend API for building detection and village infrastructure planning",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
PROJECTS_DIR = OUTPUTS_DIR / "projects"
UPLOADS_DIR = BASE_DIR / "uploads"
PIPELINE_ENTRYPOINT = BASE_DIR / "src" / "run_pipeline.py"
DEFAULT_WEIGHTS = BASE_DIR / "models" / "building_unet_resnet34.pth"
WORKER_POLL_SECONDS = 5
RUNNING_PROJECTS: Set[str] = set()
RUNNING_LOCK = threading.Lock()
WORKER_STOP_EVENT = threading.Event()


def _project_dir(project_id: str) -> Path:
    return PROJECTS_DIR / project_id


def _status_path(project_id: str) -> Path:
    return _project_dir(project_id) / "status.json"


def _write_status(project_id: str, status: str, **extra: Any) -> None:
    d = _project_dir(project_id)
    d.mkdir(parents=True, exist_ok=True)
    payload = {
        "project_id": project_id,
        "status": status,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    payload.update(extra)
    _status_path(project_id).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _sync_db_status(project_id, status, payload)


def _sync_db_status(project_id: str, status: str, payload: Dict[str, Any]) -> None:
    db = SessionLocal()
    try:
        row = db.query(ProjectRun).filter(ProjectRun.id == project_id).first()
        if row is None:
            row = ProjectRun(
                id=project_id,
                status=status,
                input_file=payload.get("input_file", ""),
                output_dir=payload.get("output_dir"),
                error_message=payload.get("error"),
                extra_metadata=payload,
            )
            db.add(row)
        else:
            row.status = status
            row.input_file = payload.get("input_file", row.input_file)
            row.output_dir = payload.get("output_dir", row.output_dir)
            row.error_message = payload.get("error", row.error_message)
            row.extra_metadata = payload
        db.commit()
    except Exception:
        db.rollback()
        logger.debug("DB status sync skipped for %s", project_id, exc_info=True)
    finally:
        db.close()


def _read_status(project_id: str) -> Dict[str, Any]:
    p = _status_path(project_id)
    if not p.exists():
        raise HTTPException(status_code=404, detail=f"Unknown project_id: {project_id}")
    return json.loads(p.read_text(encoding="utf-8"))


def _segments_from_points(points: List[List[float]]) -> List[List[List[float]]]:
    return [[points[i], points[i + 1]] for i in range(len(points) - 1)]


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _claim_project(project_id: str) -> bool:
    with RUNNING_LOCK:
        if project_id in RUNNING_PROJECTS:
            return False
        RUNNING_PROJECTS.add(project_id)
        return True


def _release_project(project_id: str) -> None:
    with RUNNING_LOCK:
        RUNNING_PROJECTS.discard(project_id)


def _persist_planning_segments(
    db: Session,
    project_id: str,
    infra_type: str,
    status: str,
    segments: List[List[List[float]]],
    cost_estimate: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None,
    replace_existing: bool = True,
) -> int:
    if replace_existing:
        db.query(InfrastructureLayer).filter(
            InfrastructureLayer.project_id == project_id,
            InfrastructureLayer.type == infra_type,
        ).delete(synchronize_session=False)
        db.commit()

    rows = []
    for seg in segments:
        if len(seg) != 2:
            continue
        geom = LineString([tuple(seg[0]), tuple(seg[1])])
        if geom.is_empty:
            continue
        rows.append(
            InfrastructureLayer(
                project_id=project_id,
                type=infra_type,
                status=status,
                cost_estimate=float(cost_estimate or 0.0),
                extra_metadata=metadata or {},
                geom=WKTElement(geom.wkt, srid=4326),
            )
        )
    if rows:
        db.bulk_save_objects(rows)
        db.commit()
    return len(rows)


def _run_queued_job_from_status(project_id: str, status_payload: Dict[str, Any]) -> bool:
    params = status_payload.get("queue_params") or {}
    input_file = params.get("input_file")
    weights_file = params.get("weights_file")
    if not input_file or not weights_file:
        _write_status(project_id, "failed", error="Queued job missing input_file/weights_file")
        return False
    _run_pipeline_job(
        project_id=project_id,
        input_path=Path(input_file),
        weights_path=Path(weights_file),
        tile_size=int(params.get("tile_size", 512)),
        threshold=float(params.get("threshold", 0.5)),
        seed=int(params.get("seed", 42)),
    )
    return True


def _ingest_project_features(
    project_id: str,
    db: Session,
    clear_existing: bool = True,
    force_reingest: bool = False,
) -> Dict[str, Any]:
    geojson_path = _project_dir(project_id) / "building_footprints.geojson"
    if not geojson_path.exists():
        raise HTTPException(status_code=404, detail=f"Footprint file not found: {geojson_path}")
    manifest_path = _project_dir(project_id) / "artifacts" / "ingestion.json"
    source_sha = _sha256_file(geojson_path)

    manifest = None
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not force_reingest and manifest.get("source_sha256") == source_sha:
            return {
                "ingested_features": int(manifest.get("feature_count", 0)),
                "ingestion_version": int(manifest.get("ingestion_version", 1)),
                "skipped": True,
                "reason": "No source changes detected",
            }

    gdf = gpd.read_file(geojson_path)
    if gdf.empty:
        return {"ingested_features": 0, "ingestion_version": 0, "skipped": False, "reason": "No geometries"}
    if gdf.crs is None:
        raise HTTPException(status_code=400, detail="Input GeoJSON has no CRS.")

    gdf_4326 = gdf.to_crs(epsg=4326)
    gdf_utm = gdf.to_crs(epsg=32614)
    gdf_4326["area_sq_m"] = gdf_utm.geometry.area
    next_version = int(manifest.get("ingestion_version", 0) + 1) if manifest else 1

    if clear_existing:
        db.query(ExtractedFeature).filter(
            ExtractedFeature.project_id == project_id,
            ExtractedFeature.type == "building",
        ).delete(synchronize_session=False)
        db.commit()

    rows = []
    for _, row in gdf_4326.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue
        rows.append(
            ExtractedFeature(
                project_id=project_id,
                ingestion_version=next_version,
                type="building",
                confidence=1.0,
                area_sq_m=float(row["area_sq_m"]),
                properties={"source": "pipeline_vectorization"},
                geom=WKTElement(geom.wkt, srid=4326),
            )
        )

    if rows:
        db.bulk_save_objects(rows)
        db.commit()

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_payload = {
        "project_id": project_id,
        "ingestion_version": next_version,
        "feature_count": len(rows),
        "source_sha256": source_sha,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
    }
    manifest_path.write_text(json.dumps(manifest_payload, indent=2), encoding="utf-8")
    return {"ingested_features": len(rows), "ingestion_version": next_version, "skipped": False}


def _run_pipeline_job(
    project_id: str,
    input_path: Path,
    weights_path: Path,
    tile_size: int,
    threshold: float,
    seed: int,
) -> None:
    if not _claim_project(project_id):
        logger.info("Project %s already running; skipping duplicate execution", project_id)
        return
    project_out = _project_dir(project_id)
    metadata_path = project_out / "artifacts" / "metadata.json"
    db = None
    try:
        _write_status(project_id, "running", input_file=str(input_path), output_dir=str(project_out))
        cmd = [
            sys.executable,
            str(PIPELINE_ENTRYPOINT),
            "--input",
            str(input_path),
            "--weights",
            str(weights_path),
            "--output-base",
            str(project_out),
            "--tile-size",
            str(tile_size),
            "--threshold",
            str(threshold),
            "--seed",
            str(seed),
            "--project-id",
            project_id,
        ]
        result = subprocess.run(cmd, cwd=str(BASE_DIR), capture_output=True, text=True)
        if result.returncode != 0:
            _write_status(project_id, "failed", error=result.stderr[-4000:], return_code=result.returncode)
            logger.error("Pipeline failed for %s: %s", project_id, result.stderr)
            return

        _write_status(
            project_id,
            "completed",
            output_dir=str(project_out),
            metadata_file=str(metadata_path),
        )
        db = SessionLocal()
        ingest_result = _ingest_project_features(project_id, db, clear_existing=True, force_reingest=False)
        _write_status(
            project_id,
            "completed_ingested",
            output_dir=str(project_out),
            metadata_file=str(metadata_path),
            ingestion=ingest_result,
        )
        logger.info("Pipeline completed for %s", project_id)
    except Exception as exc:
        _write_status(project_id, "failed", error=str(exc))
        logger.exception("Unhandled pipeline error for %s: %s", project_id, exc)
    finally:
        if db is not None:
            db.close()
        _release_project(project_id)


def _worker_loop() -> None:
    logger.info("Queue worker started")
    while not WORKER_STOP_EVENT.is_set():
        try:
            for status_file in PROJECTS_DIR.glob("*/status.json"):
                payload = json.loads(status_file.read_text(encoding="utf-8"))
                project_id = str(payload.get("project_id"))
                if payload.get("status") != "queued":
                    continue
                _run_queued_job_from_status(project_id, payload)
        except Exception:
            logger.exception("Queue worker iteration failed")
        WORKER_STOP_EVENT.wait(WORKER_POLL_SECONDS)
    logger.info("Queue worker stopped")


@app.on_event("startup")
async def startup_event() -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        init_db()
    except Exception as exc:
        logger.warning("Database init skipped/failed: %s", exc)
    WORKER_STOP_EVENT.clear()
    worker = threading.Thread(target=_worker_loop, daemon=True, name="project-queue-worker")
    worker.start()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    WORKER_STOP_EVENT.set()


@app.get("/")
def root() -> Dict[str, str]:
    return {"status": "Backend running", "service": "Aerovillage API", "version": "1.2.0"}


@app.get("/api/health")
async def health_check() -> Dict[str, str]:
    return {"status": "healthy", "service": "Aerovillage API"}


@app.get("/api/projects/{project_id}/status")
async def project_status(project_id: str) -> Dict[str, Any]:
    return _read_status(project_id)


@app.get("/api/projects")
async def list_projects(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    if limit < 1 or limit > 500:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 500")
    if offset < 0:
        raise HTTPException(status_code=400, detail="offset must be >= 0")

    query = db.query(ProjectRun)
    if status:
        query = query.filter(ProjectRun.status == status)
    total = query.count()
    rows = query.order_by(ProjectRun.updated_at.desc()).offset(offset).limit(limit).all()
    return {
        "projects": [
            {
                "project_id": r.id,
                "status": r.status,
                "input_file": r.input_file,
                "output_dir": r.output_dir,
                "error_message": r.error_message,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            }
            for r in rows
        ],
        "pagination": {"limit": limit, "offset": offset, "returned": len(rows), "total": total},
    }


@app.get("/api/projects/{project_id}/artifacts")
async def project_artifacts(project_id: str) -> Dict[str, Any]:
    project_out = _project_dir(project_id)
    if not project_out.exists():
        raise HTTPException(status_code=404, detail=f"Unknown project_id: {project_id}")
    artifacts = {
        "building_mask": str(project_out / "building_mask.tif"),
        "building_confidence": str(project_out / "building_confidence.tif"),
        "footprints_geojson": str(project_out / "building_footprints.geojson"),
        "stats_csv": str(project_out / "building_stats.csv"),
        "metadata_json": str(project_out / "artifacts" / "metadata.json"),
    }
    return {
        "project_id": project_id,
        "exists": {k: Path(v).exists() for k, v in artifacts.items()},
        "artifacts": artifacts,
    }


@app.post("/api/projects/{project_id}/ingest")
async def ingest_project_outputs(
    project_id: str,
    clear_existing: bool = True,
    force_reingest: bool = False,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    status = _read_status(project_id)
    if status.get("status") not in {"completed", "completed_ingested"}:
        raise HTTPException(status_code=409, detail="Project pipeline is not completed yet.")
    try:
        result = _ingest_project_features(
            project_id,
            db,
            clear_existing=clear_existing,
            force_reingest=force_reingest,
        )
        _write_status(project_id, "completed_ingested", ingestion=result)
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"status": "success", "project_id": project_id, **result}


@app.get("/api/projects/{project_id}/features")
async def get_project_features(
    project_id: str,
    limit: int = 1000,
    offset: int = 0,
    ingestion_version: Optional[int] = None,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    if limit < 1 or limit > 10000:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 10000")
    if offset < 0:
        raise HTTPException(status_code=400, detail="offset must be >= 0")

    if db.bind.dialect.name == "postgresql":
        where_sql = "project_id = :project_id"
        params: Dict[str, Any] = {"project_id": project_id, "limit": limit, "offset": offset}
        if ingestion_version is not None:
            where_sql += " AND ingestion_version = :ingestion_version"
            params["ingestion_version"] = ingestion_version
        rows = db.execute(
            text(
                "SELECT id, project_id, type, confidence, area_sq_m, ingestion_version, "
                "ST_AsGeoJSON(geom) AS geometry "
                "FROM extracted_features "
                f"WHERE {where_sql} "
                "ORDER BY id "
                "LIMIT :limit OFFSET :offset"
            ),
            params,
        ).mappings().all()

        features = [
            {
                "type": "Feature",
                "geometry": json.loads(r["geometry"]) if r.get("geometry") else None,
                "properties": {
                    "id": str(r["id"]),
                    "project_id": r["project_id"],
                    "feature_type": r["type"],
                    "confidence": r["confidence"],
                    "area_sq_m": r["area_sq_m"],
                    "ingestion_version": r["ingestion_version"],
                },
            }
            for r in rows
        ]
    else:
        query = db.query(ExtractedFeature).filter(ExtractedFeature.project_id == project_id)
        if ingestion_version is not None:
            query = query.filter(ExtractedFeature.ingestion_version == ingestion_version)
        rows = query.offset(offset).limit(limit).all()

        features = []
        for row in rows:
            try:
                geom = to_shape(row.geom)
                geometry = geom.__geo_interface__
            except Exception:
                geometry = None
            features.append(
                {
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": {
                        "id": str(row.id),
                        "project_id": row.project_id,
                        "feature_type": row.type,
                        "confidence": row.confidence,
                        "area_sq_m": row.area_sq_m,
                        "ingestion_version": row.ingestion_version,
                    },
                }
            )

    return {
        "type": "FeatureCollection",
        "project_id": project_id,
        "pagination": {"limit": limit, "offset": offset, "returned": len(features)},
        "features": features,
    }


@app.get("/api/projects/{project_id}/features/summary")
async def get_project_feature_summary(project_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    rows = db.query(ExtractedFeature).filter(ExtractedFeature.project_id == project_id).all()
    if not rows:
        raise HTTPException(status_code=404, detail=f"No ingested features found for project_id {project_id}")
    total_area = sum(float(r.area_sq_m or 0.0) for r in rows)
    latest_version = max(int(r.ingestion_version or 1) for r in rows)
    return {
        "project_id": project_id,
        "feature_count": len(rows),
        "total_area_sq_m": total_area,
        "average_area_sq_m": total_area / len(rows),
        "latest_ingestion_version": latest_version,
    }


@app.get("/api/projects/{project_id}/planning")
async def get_project_planning_layers(
    project_id: str,
    infra_type: Optional[str] = None,
    limit: int = 5000,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    if limit < 1 or limit > 20000:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 20000")
    if offset < 0:
        raise HTTPException(status_code=400, detail="offset must be >= 0")

    if db.bind.dialect.name == "postgresql":
        where_sql = "project_id = :project_id"
        params: Dict[str, Any] = {"project_id": project_id, "limit": limit, "offset": offset}
        if infra_type:
            where_sql += " AND type = :infra_type"
            params["infra_type"] = infra_type
        rows = db.execute(
            text(
                "SELECT id, project_id, type, status, cost_estimate, extra_metadata, ST_AsGeoJSON(geom) AS geometry "
                "FROM infrastructure_layers "
                f"WHERE {where_sql} "
                "ORDER BY id "
                "LIMIT :limit OFFSET :offset"
            ),
            params,
        ).mappings().all()
        features = [
            {
                "type": "Feature",
                "geometry": json.loads(r["geometry"]) if r.get("geometry") else None,
                "properties": {
                    "id": str(r["id"]),
                    "project_id": r["project_id"],
                    "infra_type": r["type"],
                    "status": r["status"],
                    "cost_estimate": r["cost_estimate"],
                    "extra_metadata": r.get("extra_metadata") or {},
                },
            }
            for r in rows
        ]
    else:
        query = db.query(InfrastructureLayer).filter(InfrastructureLayer.project_id == project_id)
        if infra_type:
            query = query.filter(InfrastructureLayer.type == infra_type)
        rows = query.offset(offset).limit(limit).all()
        features = []
        for row in rows:
            try:
                geom = to_shape(row.geom)
                geometry = geom.__geo_interface__
            except Exception:
                geometry = None
            features.append(
                {
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": {
                        "id": str(row.id),
                        "project_id": row.project_id,
                        "infra_type": row.type,
                        "status": row.status,
                        "cost_estimate": row.cost_estimate,
                        "extra_metadata": row.extra_metadata or {},
                    },
                }
            )

    return {
        "type": "FeatureCollection",
        "project_id": project_id,
        "pagination": {"limit": limit, "offset": offset, "returned": len(features)},
        "features": features,
    }


@app.get("/api/buildings")
async def get_buildings(project_id: Optional[str] = None) -> Dict[str, Any]:
    if project_id:
        geojson_path = _project_dir(project_id) / "building_footprints.geojson"
    else:
        geojson_path = OUTPUTS_DIR / "building_footprints.geojson"
    if not geojson_path.exists():
        raise HTTPException(status_code=404, detail="Building data not found")
    with geojson_path.open("r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/statistics")
async def get_statistics(project_id: Optional[str] = None) -> Dict[str, float]:
    stats_path = _project_dir(project_id) / "building_stats.csv" if project_id else OUTPUTS_DIR / "building_stats.csv"
    if not stats_path.exists():
        raise HTTPException(status_code=404, detail=f"Stats file not found: {stats_path}")
    try:
        import pandas as pd

        df = pd.read_csv(stats_path)
        area = df["area_m2"] if "area_m2" in df.columns else pd.Series(dtype=float)
        return {
            "total_buildings": float(len(df)),
            "total_area_m2": float(area.sum()) if not area.empty else 0.0,
            "average_area_m2": float(area.mean()) if not area.empty else 0.0,
            "min_area_m2": float(area.min()) if not area.empty else 0.0,
            "max_area_m2": float(area.max()) if not area.empty else 0.0,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/upload")
async def upload_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    run_pipeline: bool = False,
    wait_for_completion: bool = False,
    weights_path: Optional[str] = None,
    tile_size: int = 512,
    threshold: float = 0.5,
    seed: int = 42,
) -> Dict[str, Any]:
    project_id = str(uuid.uuid4())
    temp_path = UPLOADS_DIR / f"{project_id}_{file.filename}"
    with temp_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    spatial_metadata = {"has_spatial": False, "crs": None, "bounds": None, "centroid": None}
    try:
        with rasterio.open(temp_path) as src:
            if src.crs:
                bounds = src.bounds
                spatial_metadata = {
                    "has_spatial": True,
                    "crs": src.crs.to_string(),
                    "bounds": [bounds.left, bounds.bottom, bounds.right, bounds.top],
                    "centroid": [(bounds.left + bounds.right) / 2, (bounds.bottom + bounds.top) / 2],
                }
    except Exception as exc:
        logger.exception("Failed reading raster metadata for %s: %s", temp_path, exc)

    _write_status(
        project_id,
        "uploaded",
        filename=file.filename,
        input_file=str(temp_path),
        has_spatial=spatial_metadata["has_spatial"],
    )

    if run_pipeline:
        resolved_weights = Path(weights_path) if weights_path else DEFAULT_WEIGHTS
        if not resolved_weights.exists():
            raise HTTPException(status_code=400, detail=f"Model weights not found: {resolved_weights}")
        if wait_for_completion:
            _run_pipeline_job(project_id, temp_path, resolved_weights, tile_size, threshold, seed)
        else:
            _write_status(
                project_id,
                "queued",
                input_file=str(temp_path),
                queue_params={
                    "input_file": str(temp_path),
                    "weights_file": str(resolved_weights),
                    "tile_size": tile_size,
                    "threshold": threshold,
                    "seed": seed,
                },
            )
            # Opportunistic immediate execution; worker still provides durability for queued runs.
            background_tasks.add_task(_run_queued_job_from_status, project_id, _read_status(project_id))

    return {
        "status": "success",
        "project_id": project_id,
        "filename": file.filename,
        "spatial_metadata": spatial_metadata,
        "pipeline_status": _read_status(project_id)["status"],
    }


@app.post("/api/spatial/expand")
async def expand_analysis(request: Dict[str, Any]) -> Dict[str, Any]:
    center = request.get("center")
    radius_km = request.get("radius", 1.0)
    if not center or len(center) != 2:
        raise HTTPException(status_code=400, detail="center must be [lon, lat]")
    return {
        "status": "accepted",
        "expanded_radius": radius_km,
        "message": "Area expansion is not implemented for production yet.",
    }


@app.post("/api/planning/sewage")
async def plan_sewage(request: Dict[str, Any]) -> Dict[str, Any]:
    buildings = request.get("buildings", [])
    project_id = request.get("project_id")
    persist = bool(request.get("persist", True))
    if len(buildings) < 2:
        raise HTTPException(status_code=400, detail="At least 2 buildings are required")

    import networkx as nx

    road_graph = nx.Graph()
    for b in buildings:
        road_graph.add_edge(tuple(b), (b[0] + 0.001, b[1] + 0.001), distance=150.0)
        road_graph.add_edge((b[0] + 0.001, b[1] + 0.001), (b[0] + 0.002, b[1] - 0.001), distance=200.0)

    dtm = DTMProcessor()
    planner = SewagePlanner(dtm)
    results = planner.plan_network(buildings, road_graph)
    segments = _segments_from_points(buildings)

    procurement = ProcurementEngine(dtm)
    estimate = procurement.estimate_project_cost("sewage", segments)
    persisted_segments = 0
    if persist and project_id:
        db = SessionLocal()
        try:
            persisted_segments = _persist_planning_segments(
                db=db,
                project_id=project_id,
                infra_type="sewage",
                status="proposed",
                segments=segments,
                cost_estimate=estimate.get("total_estimate"),
                metadata={"planner": "sewage", "algorithm": "elevation_aware_shortest_path"},
                replace_existing=True,
            )
        finally:
            db.close()

    return {
        "status": "success",
        "planner": "sewage",
        "results": results,
        "paths": segments,
        "budgetary_estimate": estimate,
        "persisted_segments": persisted_segments,
    }


@app.post("/api/planning/electricity")
async def plan_electricity(request: Dict[str, Any]) -> Dict[str, Any]:
    buildings = request.get("buildings", [])
    project_id = request.get("project_id")
    persist = bool(request.get("persist", True))
    if len(buildings) < 2:
        raise HTTPException(status_code=400, detail="At least 2 buildings are required")

    dtm = DTMProcessor()
    planner = ElectricityPlanner()
    results = planner.optimize_grid(buildings)
    segments = _segments_from_points(buildings)

    procurement = ProcurementEngine(dtm)
    estimate = procurement.estimate_project_cost("electricity", segments)
    persisted_segments = 0
    if persist and project_id:
        db = SessionLocal()
        try:
            persisted_segments = _persist_planning_segments(
                db=db,
                project_id=project_id,
                infra_type="electricity",
                status="proposed",
                segments=segments,
                cost_estimate=estimate.get("total_estimate"),
                metadata={"planner": "electricity", "algorithm": "clustered_mst"},
                replace_existing=True,
            )
        finally:
            db.close()

    return {
        "status": "success",
        "planner": "electricity",
        "results": results,
        "paths": segments,
        "budgetary_estimate": estimate,
        "persisted_segments": persisted_segments,
    }


@app.post("/api/rag/ingest")
async def ingest_policy(request: Dict[str, Any], db: Session = Depends(get_db)) -> Dict[str, Any]:
    title = request.get("title", "Unnamed Policy")
    content = request.get("content", "")
    source = request.get("source", "Manual Upload")
    project_id = request.get("project_id")
    rag = HybridRAGService(db=db, base_dir=BASE_DIR)
    chunks = rag.ingest_policy(title=title, content=content, source=source, project_id=project_id)
    return {"status": "success", "message": f"Policy '{title}' indexed into {chunks} chunks."}


@app.post("/api/rag/query")
@app.post("/api/rag/explain")
async def explain_compliance(request: Dict[str, Any], db: Session = Depends(get_db)) -> Dict[str, Any]:
    query = (request.get("query") or request.get("question") or "").strip()
    project_id = (request.get("project_id") or "global").strip()
    if not query:
        raise HTTPException(status_code=400, detail="query is required")
    rag = HybridRAGService(db=db, base_dir=BASE_DIR)
    result = rag.query(project_id=project_id, question=query)
    return {"status": "success", **result}


@app.post("/api/procurement/estimate")
async def estimate_costs(request: Dict[str, Any]) -> Dict[str, Any]:
    infra_type = request.get("type", "sewage")
    segments = request.get("segments", [])
    dtm = DTMProcessor()
    engine = ProcurementEngine(dtm)
    estimate = engine.estimate_project_cost(infra_type, segments)
    return {"status": "success", "estimate": estimate}


@app.post("/api/simulation/flood")
async def run_flood_simulation(request: Dict[str, Any]) -> Dict[str, Any]:
    bounds = request.get("bounds", [78.96, 20.59, 78.97, 20.60])
    rainfall_mm = request.get("rainfall", 100.0)
    dtm = DTMProcessor()
    sim = HydrologySimulator(dtm)
    results = sim.simulate_flood(bounds, rainfall_mm)
    return {"status": "success", "simulation_type": "flood", "results": results}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
