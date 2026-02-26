import argparse
import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import rasterio

from building_detect import run_inference
from compute_stats import compute_spatial_stats
from export_web_geojson import export_for_web
from merge_masks import merge_masks
from tile_ortho import tile_orthophoto
from vectorize_mask import vectorize
from verify_results import verify_mask


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_input_raster(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Input raster not found: {path}")
    with rasterio.open(path) as src:
        if src.crs is None:
            raise ValueError("Input raster has no CRS.")
        if src.transform.a == 0 or src.transform.e == 0:
            raise ValueError("Input raster has invalid resolution.")
        return {
            "crs": src.crs.to_string(),
            "width": src.width,
            "height": src.height,
            "resolution": [src.transform.a, abs(src.transform.e)],
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run end-to-end geospatial building extraction pipeline.")
    parser.add_argument("--input", required=True, help="Input orthophoto path (GeoTIFF).")
    parser.add_argument("--weights", default="models/building_unet_resnet34.pth", help="Model weights path.")
    parser.add_argument("--tile-size", type=int, default=512, help="Tile size in pixels.")
    parser.add_argument("--threshold", type=float, default=0.5, help="Sigmoid threshold.")
    parser.add_argument("--output-base", default="outputs", help="Base output directory.")
    parser.add_argument("--web-geojson-out", default="", help="Optional web GeoJSON output path (EPSG:4326).")
    parser.add_argument("--project-id", default="", help="Optional project identifier for traceability.")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic seed.")
    return parser


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    logger = logging.getLogger("pipeline")
    args = build_parser().parse_args()

    input_path = Path(args.input)
    weights_path = Path(args.weights)
    base_dir = Path(args.output_base)
    tiles_dir = base_dir / "tiles"
    mask_tiles_dir = base_dir / "mask_tiles"
    confidence_tiles_dir = base_dir / "confidence_tiles"
    artifacts_dir = base_dir / "artifacts"

    for d in [base_dir, tiles_dir, mask_tiles_dir, confidence_tiles_dir, artifacts_dir]:
        d.mkdir(parents=True, exist_ok=True)

    if not weights_path.exists():
        raise FileNotFoundError(f"Model weights not found: {weights_path}")

    raster_meta = validate_input_raster(input_path)
    logger.info("Input validated: CRS=%s size=%sx%s", raster_meta["crs"], raster_meta["width"], raster_meta["height"])

    tile_count = tile_orthophoto(str(input_path), str(tiles_dir), tile_size=args.tile_size)
    logger.info("Tiling complete: %s tiles", tile_count)

    run_inference(
        tile_dir=str(tiles_dir),
        output_dir=str(mask_tiles_dir),
        weights_path=str(weights_path),
        threshold=args.threshold,
        confidence_output_dir=str(confidence_tiles_dir),
        seed=args.seed,
    )
    logger.info("Inference complete for mask and confidence tiles")

    merged_mask_path = base_dir / "building_mask.tif"
    merged_confidence_path = base_dir / "building_confidence.tif"
    merge_masks(str(mask_tiles_dir), str(merged_mask_path), pattern="tile_*.tif", dtype="uint8", nodata=0)
    merge_masks(
        str(confidence_tiles_dir), str(merged_confidence_path), pattern="tile_*.tif", dtype="float32", nodata=0.0
    )
    logger.info("Merged mask and confidence rasters")

    footprints_path = base_dir / "building_footprints.geojson"
    vectorize(str(merged_mask_path), str(footprints_path))
    compute_spatial_stats(str(footprints_path), out_csv=str(base_dir / "building_stats.csv"))
    if args.web_geojson_out:
        export_for_web(str(footprints_path), args.web_geojson_out)
    verify_mask(str(merged_mask_path))
    logger.info("Vectorization/statistics/export complete")

    metadata = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "input_file": str(input_path),
        "input_sha256": sha256_file(input_path),
        "weights_file": str(weights_path),
        "weights_sha256": sha256_file(weights_path),
        "seed": args.seed,
        "project_id": args.project_id or None,
        "threshold": args.threshold,
        "tile_size": args.tile_size,
        "raster": raster_meta,
        "outputs": {
            "mask": str(merged_mask_path),
            "confidence": str(merged_confidence_path),
            "footprints": str(footprints_path),
            "stats_csv": str(base_dir / "building_stats.csv"),
        },
    }
    metadata_path = artifacts_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    logger.info("Metadata written: %s", metadata_path)


if __name__ == "__main__":
    main()
