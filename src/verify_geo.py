import rasterio

def check_metadata(file_path):
    with rasterio.open(file_path) as src:
        print(f"CRS: {src.crs}")
        print(f"Size: {src.width}x{src.height}")
        print(f"Bands: {src.count}")
        print(f"Dtype: {src.dtypes}")
        print(f"Transform: {src.transform}")

def convert_to_cog(input_path, output_path):
    with rasterio.open(input_path) as src:
        profile = src.profile.copy()
        # COG requirements: tiled, compressed, overviews
        profile.update({
            'driver': 'GTiff',
            'tiled': True,
            'blockxsize': 512,
            'blockysize': 512,
            'compress': 'deflate',
            'interleave': 'pixel',
            'photometric': 'rgb' if src.count >= 3 else 'minisblack'
        })
        
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(src.read())
            # Overviews are usually added for COG but for a simple hackathon this might be enough
            # or we can add them:
            # dst.build_overviews([2, 4, 8, 16], Resampling.nearest)
            # dst.update_tags(ns='rio_overview', resampling='nearest')

if __name__ == "__main__":
    check_metadata('data/processed/orthophoto.tif')
    convert_to_cog('data/processed/orthophoto.tif', 'data/processed/orthophoto_cog.tif')
