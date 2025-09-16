import rasterio
import numpy as np
from pathlib import Path

FILE = r"D:\Desktop\uccellina_multispectral_normalised.tif"
OUT_DIR = Path(r"D:\Desktop\uccellina_audit")
OUT_DIR.mkdir(parents=True, exist_ok=True)

with rasterio.open(FILE) as ds:
    red = ds.read(1).astype("float32")
    green = ds.read(2).astype("float32")
    blue = ds.read(3).astype("float32")
    red_edge = ds.read(4).astype("float32")
    nir = ds.read(5).astype("float32")
    profile = ds.profile

# Normalizza valori tra 0–1
red /= 255.0
green /= 255.0
blue /= 255.0
nir /= 255.0
red_edge /= 255.0

# Indici
ndvi = (nir - red) / (nir + red + 1e-6)
ndwi = (green - nir) / (green + nir + 1e-6)
brightness = (red + green + blue) / 3.0

# Mask acqua
mask_water = ndwi > 0.2

# Mask vegetazione
mask_veg = ndvi > 0.2

# Mask sabbia
mask_sand = (ndvi < 0.1) & (brightness > 0.4)

# AOI = tutto tranne acqua
mask_aoi = ~mask_water

# IGNORE = acqua ∪ sabbia
mask_ignore = mask_water | mask_sand

# Funzione salvataggio
def save_mask(arr, name):
    out_profile = profile.copy()
    out_profile.update(dtype=rasterio.uint8, count=1)
    out_file = OUT_DIR / name
    with rasterio.open(out_file, "w", **out_profile) as dst:
        dst.write(arr.astype("uint8"), 1)
    print(f"✓ Saved {out_file}")

save_mask(mask_aoi, "mask_aoi.tif")
save_mask(mask_ignore, "mask_ignore.tif")
