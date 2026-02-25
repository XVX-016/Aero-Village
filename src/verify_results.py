import rasterio
import numpy as np

def verify_mask(mask_path):
    with rasterio.open(mask_path) as src:
        mask = src.read(1)
        print(f"Mask shape: {mask.shape}")
        building_pixels = np.sum(mask > 0)
        total_pixels = mask.size
        coverage = (building_pixels / total_pixels) * 100
        print(f"Detected building pixels: {building_pixels}")
        print(f"Building coverage: {coverage:.2f}%")
        
        if building_pixels > 0:
            print("Verification successful: Buildings detected.")
        else:
            print("Verification warning: No buildings detected. Check input data and model.")

if __name__ == "__main__":
    verify_mask("outputs/building_mask.tif")
