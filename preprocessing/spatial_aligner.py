from pathlib import Path

import rasterio
from rasterio.warp import Resampling, reproject


def align_raster_to_reference(input_path, reference_path, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(input_path) as src, rasterio.open(reference_path) as reference:
        nodata = reference.nodata
        profile = reference.meta.copy()
        profile.update(
            {
                "crs": reference.crs,
                "transform": reference.transform,
                "width": reference.width,
                "height": reference.height,
                "nodata": nodata,
                "count": src.count,
                "dtype": src.dtypes[0],
            }
        )

        with rasterio.open(output_path, "w", **profile) as dst:
            for band_index in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, band_index),
                    destination=rasterio.band(dst, band_index),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=reference.transform,
                    dst_crs=reference.crs,
                    resampling=Resampling.bilinear,
                    src_nodata=src.nodata,
                    dst_nodata=nodata,
                    init_dest_nodata=True,
                )
