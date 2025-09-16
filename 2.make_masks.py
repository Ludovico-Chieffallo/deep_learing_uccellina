import rasterio
import numpy as np
from pathlib import Path

FILE = r"D:\Desktop\uccellina_multispectral_normalised.tif"
OUT_DIR = Path(r"D:\Desktop\uccellina_audit")
OUT_DIR.mkdir(parents=True, exist_ok=True)

with rasterio.open(FILE) as ds:
    profile = ds.profile
    profile.update(dtype=rasterio.uint8, count=2, compress="lzw")

    out_file = OUT_DIR / "masks.tif"
    with rasterio.open(out_file, "w", **profile) as dst:
        # 2 layer: 1=AOI, 2=IGNORE
        for ji, window in ds.block_windows(1):
            red = ds.read(1, window=window).astype("float32") / 255.0
            green = ds.read(2, window=window).astype("float32") / 255.0
            blue = ds.read(3, window=window).astype("float32") / 255.0
            red_edge = ds.read(4, window=window).astype("float32") / 255.0
            nir = ds.read(5, window=window).astype("float32") / 255.0

            ndvi = (nir - red) / (nir + red + 1e-6)
            ndwi = (green - nir) / (green + nir + 1e-6)
            brightness = (red + green + blue) / 3.0

            mask_water = ndwi > 0.2
            mask_veg = ndvi > 0.2
            mask_sand = (ndvi < 0.1) & (brightness > 0.4)

            mask_aoi = (~mask_water).astype("uint8")
            mask_ignore = (mask_water | mask_sand).astype("uint8")

            dst.write(mask_aoi, 1, window=window)
            dst.write(mask_ignore, 2, window=window)

print(f"✓ Saved {out_file}")
