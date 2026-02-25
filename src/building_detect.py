import rasterio
import numpy as np
import torch
import segmentation_models_pytorch as smp
import os
import argparse
import random
from typing import Optional

DEFAULT_TILE_DIR = "tiles"
DEFAULT_OUTPUT_DIR = "outputs"
DEFAULT_WEIGHTS_PATH = "models/building_unet_resnet34.pth"


def load_model(device: str, weights_path: str):
    model = smp.Unet(
        encoder_name="resnet34",
        encoder_weights=None,
        in_channels=3,
        classes=1,
    )
    if not os.path.exists(weights_path):
        raise FileNotFoundError(
            f"Model weights not found at: {weights_path}. "
            "Provide trained weights with --weights."
        )
    state_dict = torch.load(weights_path, map_location=device)
    model.load_state_dict(state_dict)
    model.eval().to(device)
    return model


def run_inference(
    tile_dir: str,
    output_dir: str,
    weights_path: str,
    threshold: float,
    confidence_output_dir: Optional[str] = None,
    seed: int = 42,
):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    model = load_model(device, weights_path)

    os.makedirs(output_dir, exist_ok=True)
    if confidence_output_dir:
        os.makedirs(confidence_output_dir, exist_ok=True)
    tiles = sorted([f for f in os.listdir(tile_dir) if f.endswith(".tif")])
    if not tiles:
        raise FileNotFoundError(f"No tiles found in {tile_dir}")
    print(f"Processing {len(tiles)} tiles...")

    for tile in tiles:
        tile_path = os.path.join(tile_dir, tile)
        with rasterio.open(tile_path) as src:
            img = src.read().astype(np.float32)
            if img.shape[0] < 3:
                raise ValueError(f"{tile_path} has {img.shape[0]} bands; expected 3.")
            img = img[:3] / 255.0
            meta = src.meta.copy()

        tensor = torch.from_numpy(img).unsqueeze(0).to(device)
        with torch.no_grad():
            pred = model(tensor)
            confidence = torch.sigmoid(pred).squeeze().cpu().numpy().astype(np.float32)
            mask = (confidence > threshold).astype(np.uint8)

        meta.update(count=1, dtype="uint8", nodata=0)
        out_path = os.path.join(output_dir, tile)
        with rasterio.open(out_path, "w", **meta) as dst:
            dst.write(mask, 1)

        if confidence_output_dir:
            conf_meta = meta.copy()
            conf_meta.update(dtype="float32", nodata=0.0)
            conf_out_path = os.path.join(confidence_output_dir, tile)
            with rasterio.open(conf_out_path, "w", **conf_meta) as conf_dst:
                conf_dst.write(confidence, 1)

    print("Building detection complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run building segmentation on raster tiles.")
    parser.add_argument("--tiles", default=DEFAULT_TILE_DIR, help="Directory with tiled GeoTIFFs.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_DIR, help="Directory for predicted mask tiles.")
    parser.add_argument("--confidence-output", default="", help="Optional directory for confidence tiles.")
    parser.add_argument("--weights", default=DEFAULT_WEIGHTS_PATH, help="Path to trained model weights.")
    parser.add_argument("--threshold", type=float, default=0.5, help="Sigmoid threshold for binary masks.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for deterministic runs.")
    args = parser.parse_args()
    run_inference(
        args.tiles,
        args.output,
        args.weights,
        args.threshold,
        confidence_output_dir=args.confidence_output or None,
        seed=args.seed,
    )
