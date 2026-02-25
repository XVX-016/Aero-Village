import rasterio
from rasterio.features import shapes
import geopandas as gpd
import os


def vectorize(mask_path, output_path):
    if not os.path.exists(mask_path):
        print(f"Error: {mask_path} not found.")
        return

    with rasterio.open(mask_path) as src:
        image = src.read(1)
        mask = (image > 0)

        results = (
            {"properties": {"raster_val": int(v)}, "geometry": s}
            for i, (s, v) in enumerate(
                shapes(image, mask=mask, transform=src.transform)
            )
        )

        geoms = list(results)
        if not geoms:
            print("No polygons found in mask.")
            return

        df = gpd.GeoDataFrame.from_features(geoms, crs=src.crs)
        df = df[df["raster_val"] > 0].copy()
        if df.empty:
            print("No positive polygons after filtering.")
            return

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        df.to_file(output_path, driver="GeoJSON")
        print(f"Vectorized {len(df)} features to {output_path}")


if __name__ == "__main__":
    vectorize("outputs/building_mask.tif", "outputs/building_footprints.geojson")
