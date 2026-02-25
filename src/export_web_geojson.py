import geopandas as gpd
import os


def export_for_web(input_path, output_path, min_area_m2=5.0):
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    gdf = gpd.read_file(input_path)
    if gdf.empty:
        print("No features found in input GeoJSON.")
        return
    if gdf.crs is None:
        raise ValueError("Input GeoJSON has no CRS and cannot be reprojected.")

    gdf_utm = gdf.to_crs(epsg=32614)
    gdf_utm["area_m2"] = gdf_utm.geometry.area
    gdf_filtered = gdf_utm[gdf_utm["area_m2"] > min_area_m2].copy()
    if gdf_filtered.empty:
        print(f"No features found larger than {min_area_m2} m2.")
        return

    gdf_web_filtered = gdf_filtered.to_crs(epsg=4326)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    gdf_web_filtered.to_file(output_path, driver="GeoJSON")
    print(f"Exported {len(gdf_web_filtered)} features to {output_path}")


if __name__ == "__main__":
    export_for_web("outputs/building_footprints.geojson", "web_demo/data/building_footprints.geojson")
