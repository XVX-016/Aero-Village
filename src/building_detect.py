import rasterio
import numpy as np
import torch
import segmentation_models_pytorch as smp
import os

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {DEVICE}")

model = smp.Unet(
    encoder_name="resnet34",
    encoder_weights="imagenet",
    in_channels=3,
    classes=1,
)
model.eval().to(DEVICE)

os.makedirs("outputs", exist_ok=True)

tiles = [f for f in os.listdir("tiles") if f.endswith(".tif")]
print(f"Processing {len(tiles)} tiles...")

for tile in tiles:
    with rasterio.open(f"tiles/{tile}") as src:
        img = src.read().astype(np.float32) / 255.0
        meta = src.meta.copy()

    img = torch.tensor(img).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        pred = model(img)
        mask = (torch.sigmoid(pred).squeeze().cpu().numpy() > 0.5).astype(np.uint8)

    meta.update(count=1, dtype="uint8")

    with rasterio.open(f"outputs/{tile}", "w", **meta) as dst:
        dst.write(mask, 1)

print("Building detection complete.")
