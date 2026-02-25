# Aerovillage: Automated Rural Property Mapping
### Aerovillage Smart Village Intelligence Platform

> **The Problem**: Manual property surveys for local Panchayats are slow, expensive, and error-prone. This creates bottlenecks in land records and delays government revenue assessment.
> **The Solution**: An automated GeoAI pipeline that converts raw drone imagery into GIS-ready building intelligence in minutes.

---

## One-Click Judge Demo
To see the AI in action without running any code:
1. Open the **`web_demo/index.html`** file in your browser.
2. View detected building footprints overlaid on raw drone imagery.
3. Click any structure to see its automated area calculation (m²).

*(Note: For best experience, use a local server like VS Code Live Server or `npx serve web_demo` due to browser security policies.)*

---

## Project Edge
- **Zero Manual Digitization**: Replaces weeks of manual ground tagging with a U-Net AI pipeline.
- **Geospatial-Native**: Preserves absolute precision (UTM Zone 14N) for immediate integration into government land portals.
- **Actionable Stats**: Automatically computes building counts and granular footprint areas.

## Sample Impact (Wynnpage Drive Survey)
- **Input Resolution**: 2cm / pixel (Ultra-High Res)
- **Validated Footprints**: 100 significant structures
- **Total Built-up Area**: 3,062.21 m²
- **Processing Time**: < 5 minutes (End-to-end)

---

## Repository Structure
- `web_demo/`: High-impact interactive map for judges.
- `src/`: Professional Python scripts for the full AI pipeline (Tiling → Inference → Vectorization).
- `data/processed/`: Analysis-ready orthophotos and masks.
- `outputs/`: Industry-standard GeoJSON and CSV spatial analytics.

---

## Power User: Full Pipeline Execution
To run the full-resolution pipeline locally:
1. `pip install -r requirements.txt`
2. `python src/run_pipeline.py --input data/processed/orthophoto_rgb.tif --weights models/building_unet_resnet34.pth`
3. Outputs include:
   - `outputs/building_mask.tif`
   - `outputs/building_confidence.tif`
   - `outputs/building_footprints.geojson`
   - `outputs/building_stats.csv`
   - `outputs/artifacts/metadata.json`

## Backend Project Runs
- Upload and queue a project-scoped run via `POST /api/upload?run_pipeline=true`.
- List projects via `GET /api/projects?status=queued&limit=50&offset=0`.
- Poll status via `GET /api/projects/{project_id}/status`.
- Fetch output file locations via `GET /api/projects/{project_id}/artifacts`.
- Ingest project footprints into PostGIS via `POST /api/projects/{project_id}/ingest`.
- Query DB-backed features via `GET /api/projects/{project_id}/features?limit=500&offset=0`.
- Query DB-backed summary via `GET /api/projects/{project_id}/features/summary`.
- Pipeline completion auto-ingests footprints into DB with idempotent source-hash checks and ingestion versioning.
- Persist planning paths by passing `project_id` to planning APIs; query via `GET /api/projects/{project_id}/planning`.

---
*“Mapping the future of rural governance, one footprint at a time.”*
