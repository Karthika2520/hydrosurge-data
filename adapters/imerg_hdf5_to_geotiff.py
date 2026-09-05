from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

from adapters.imerg_hdf5_adapter import read_imerg_hdf5


def convert_imerg_to_geotiff(input_path, output_path):
    data = read_imerg_hdf5(input_path)

    precipitation = data["precipitation"]
    lat = data["lat"]
    lon = data["lon"]

    # IMERG latitude is ascending.
    # GeoTIFF convention expects north at the top,
    # so reverse the latitude axis.
    precipitation = np.flipud(precipitation)

    lon_resolution = float(np.mean(np.diff(lon)))
    lat_resolution = float(np.mean(np.diff(lat)))

    west = float(lon[0] - lon_resolution / 2)
    north = float(lat[-1] + lat_resolution / 2)

    transform = from_origin(
        west,
        north,
        lon_resolution,
        lat_resolution,
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(
        output_path,
        "w",
        driver="GTiff",
        height=precipitation.shape[0],
        width=precipitation.shape[1],
        count=1,
        dtype="float32",
        crs="EPSG:4326",
        transform=transform,
        nodata=-9999.0,
        compress="deflate",
    ) as dst:

        output_data = np.where(
            np.isnan(precipitation),
            -9999.0,
            precipitation,
        ).astype("float32")

        dst.write(output_data, 1)

        dst.update_tags(
            source=data["source"],
            variable="precipitation",
            unit=data["unit"],
            observed_at=data["observed_at"],
            native_resolution=data["native_resolution"],
        )

    return output_path