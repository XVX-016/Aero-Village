import rasterio
import os

src_path = "data/processed/orthophoto.tif"
dst_path = "data/processed/orthophoto_rgb.tif"

if not os.path.exists(src_path):
    print(f"Error: {src_path} not found.")
else:
    with rasterio.open(src_path) as src:
        # Read the first three bands (RGB)
        img = src.read([1, 2, 3])
        meta = src.meta.copy()

    meta.update(count=3)

    with rasterio.open(dst_path, "w", **meta) as dst:
        dst.write(img)

    print("Saved RGB orthophoto:", dst_path)
