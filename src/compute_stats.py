import os
import geopandas as gpd


def compute_spatial_stats(geojson_path, out_csv="outputs/building_stats.csv", min_area_m2=25.0):
    if not os.path.exists(geojson_path):
        print(f"Error: {geojson_path} not found.")
        return

    gdf = gpd.read_file(geojson_path)
    if gdf.empty:
        print("No features found in input GeoJSON.")
        return
    if gdf.crs is None:
        raise ValueError("Input GeoJSON has no CRS. Area calculations require a valid CRS.")

    if str(gdf.crs) != "EPSG:32614":
        gdf = gdf.to_crs(epsg=32614)

    gdf["area_m2"] = gdf.geometry.area
    gdf_filtered = gdf[gdf["area_m2"] > min_area_m2].copy()
    if gdf_filtered.empty:
        print(f"No features found larger than {min_area_m2} m2.")
        return

    print("--- SPATIAL INTELLIGENCE REPORT ---")
    print(f"Total Buildings Detected: {len(gdf_filtered)}")
    print(f"Total Building Footprint Area: {gdf_filtered['area_m2'].sum():.2f} m2")
    print(f"Average Building Size: {gdf_filtered['area_m2'].mean():.2f} m2")
    print(f"Smallest Building: {gdf_filtered['area_m2'].min():.2f} m2")
    print(f"Largest Building: {gdf_filtered['area_m2'].max():.2f} m2")
    print("-----------------------------------")

    os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)
    gdf_filtered[["area_m2"]].to_csv(out_csv, index=False)
    print(f"Saved stats to {out_csv}")


if __name__ == "__main__":
    compute_spatial_stats("outputs/building_footprints.geojson")
