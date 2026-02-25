import glob
import os

import rasterio
from rasterio.merge import merge


def merge_masks(input_dir, output_path, pattern="tile_*.tif", dtype="uint8", nodata=0):
    files = glob.glob(os.path.join(input_dir, pattern))
    if not files:
        print("No files found to merge.")
        return

    src_files_to_mosaic = [rasterio.open(f) for f in sorted(files) if os.path.basename(f) != os.path.basename(output_path)]
    if not src_files_to_mosaic:
        print("No matching tile files found to merge.")
        return
    mosaic, out_trans = merge(src_files_to_mosaic, nodata=nodata)

    out_meta = src_files_to_mosaic[0].meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": out_trans,
        "count": 1,
        "compress": "deflate",
        "dtype": dtype,
        "nodata": nodata
    })

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with rasterio.open(output_path, "w", **out_meta) as dest:
        dest.write(mosaic.astype(dtype))

    for src in src_files_to_mosaic:
        src.close()

    print(f"Saved merged mask to: {output_path}")


if __name__ == "__main__":
    merge_masks("outputs", "outputs/building_mask.tif")
