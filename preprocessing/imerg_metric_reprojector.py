from pathlib import Path

import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling


def reproject_to_metric_crs(
    input_path,
    output_path,
    target_crs="EPSG:32644",
):
    input_path = Path(input_path)
    output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(input_path) as src:

        transform, width, height = calculate_default_transform(
            src.crs,
            target_crs,
            src.width,
            src.height,
            *src.bounds,
        )

        profile = src.profile.copy()

        profile.update(
            {
                "crs": target_crs,
                "transform": transform,
                "width": width,
                "height": height,
                "nodata": -9999.0,
                "dtype": "float32",
            }
        )

        with rasterio.open(output_path, "w", **profile) as dst:

            reproject(
                source=rasterio.band(src, 1),
                destination=rasterio.band(dst, 1),
                src_transform=src.transform,
                src_crs=src.crs,
                src_nodata=src.nodata,
                dst_transform=transform,
                dst_crs=target_crs,
                dst_nodata=-9999.0,
                resampling=Resampling.nearest,
            )

            dst.update_tags(**src.tags())

            dst.update_tags(
                target_crs=target_crs,
                reprojection="EPSG:4326 to metric CRS",
            )

    return output_path