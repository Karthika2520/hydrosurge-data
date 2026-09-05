from pathlib import Path

import rasterio
from rasterio.warp import Resampling, calculate_default_transform, reproject


def normalize_raster(input_path, output_path, target_crs="EPSG:4326"):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(input_path) as src:
        nodata = src.nodata
        transform, width, height = calculate_default_transform(
            src.crs,
            target_crs,
            src.width,
            src.height,
            *src.bounds,
        )
        profile = src.meta.copy()
        profile.update(
            {
                "crs": target_crs,
                "transform": transform,
                "width": width,
                "height": height,
                "nodata": nodata,
            }
        )

        with rasterio.open(output_path, "w", **profile) as dst:
            for band_index in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, band_index),
                    destination=rasterio.band(dst, band_index),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=target_crs,
                    resampling=Resampling.nearest,
                    src_nodata=nodata,
                    dst_nodata=nodata,
                    init_dest_nodata=True,
                )
