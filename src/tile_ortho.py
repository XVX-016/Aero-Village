import os

import rasterio
from rasterio.windows import Window


def tile_orthophoto(src_path: str, out_dir: str, tile_size: int = 512) -> int:
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"Orthophoto not found: {src_path}")
    os.makedirs(out_dir, exist_ok=True)

    tiles_written = 0
    with rasterio.open(src_path) as src:
        if src.crs is None:
            raise ValueError("Input orthophoto has no CRS.")
        if src.transform.a == 0 or src.transform.e == 0:
            raise ValueError("Input orthophoto has invalid resolution transform.")

        meta = src.meta.copy()
        width, height = src.width, src.height

        for y in range(0, height, tile_size):
            for x in range(0, width, tile_size):
                win_width = min(tile_size, width - x)
                win_height = min(tile_size, height - y)
                window = Window(x, y, win_width, win_height)
                transform = src.window_transform(window)
                tile = src.read(window=window)

                meta.update({"height": int(win_height), "width": int(win_width), "transform": transform})
                out_path = os.path.join(out_dir, f"tile_{x}_{y}.tif")
                with rasterio.open(out_path, "w", **meta) as dst:
                    dst.write(tile)
                tiles_written += 1

    return tiles_written


if __name__ == "__main__":
    count = tile_orthophoto("data/processed/orthophoto_rgb.tif", "tiles", tile_size=512)
    print(f"Tiling complete. Wrote {count} tiles.")
