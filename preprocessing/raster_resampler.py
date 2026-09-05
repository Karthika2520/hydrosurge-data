from pathlib import Path

import rasterio
from pyproj import Geod
from rasterio.transform import Affine
from rasterio.warp import Resampling, reproject


def _pixel_size_crs_units(transform):
    return abs(transform.a), abs(transform.e)


def _meters_per_crs_unit(crs, center_x, center_y):
    if crs.is_projected:
        return 1.0, 1.0

    geod = Geod(ellps="WGS84")
    _, _, east_m = geod.inv(center_x, center_y, center_x + 1.0, center_y)
    _, _, north_m = geod.inv(center_x, center_y, center_x, center_y + 1.0)
    return abs(east_m), abs(north_m)


def _center(bounds):
    return (
        (bounds.left + bounds.right) / 2.0,
        (bounds.bottom + bounds.top) / 2.0,
    )


def resample_raster(input_path, output_path, target_resolution_m):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(input_path) as src:
        nodata = src.nodata
        current_res_x, current_res_y = _pixel_size_crs_units(src.transform)
        if current_res_x == 0 or current_res_y == 0:
            raise ValueError("Input raster has zero pixel resolution")

        center_x, center_y = _center(src.bounds)
        meters_per_x, meters_per_y = _meters_per_crs_unit(
            src.crs, center_x, center_y
        )
        target_res_x = target_resolution_m / meters_per_x
        target_res_y = target_resolution_m / meters_per_y

        width = max(
            1, int(round((src.bounds.right - src.bounds.left) / target_res_x))
        )
        height = max(
            1, int(round((src.bounds.top - src.bounds.bottom) / target_res_y))
        )
        transform = Affine(
            target_res_x,
            0.0,
            src.bounds.left,
            0.0,
            -target_res_y,
            src.bounds.top,
        )

        profile = src.meta.copy()
        profile.update(
            {
                "crs": src.crs,
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
                    dst_crs=src.crs,
                    resampling=Resampling.bilinear,
                    src_nodata=nodata,
                    dst_nodata=nodata,
                    init_dest_nodata=True,
                )
