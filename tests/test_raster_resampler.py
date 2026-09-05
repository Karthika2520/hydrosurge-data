from pathlib import Path

import numpy as np
import rasterio
from pyproj import Geod

from preprocessing.raster_resampler import resample_raster

NODATA = -9999.0
TARGET_RESOLUTION_M = 1000.0
RESOLUTION_TOLERANCE_M = 1.0

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "normalized_rainfall.tif"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "resampled_rainfall.tif"


def _pixel_resolution_m(dataset):
    center_x = (dataset.bounds.left + dataset.bounds.right) / 2.0
    center_y = (dataset.bounds.bottom + dataset.bounds.top) / 2.0
    pixel_width = abs(dataset.transform.a)
    pixel_height = abs(dataset.transform.e)

    if dataset.crs.is_projected:
        return pixel_width, pixel_height

    geod = Geod(ellps="WGS84")
    _, _, res_x_m = geod.inv(
        center_x, center_y, center_x + pixel_width, center_y
    )
    _, _, res_y_m = geod.inv(
        center_x, center_y, center_x, center_y + pixel_height
    )
    return abs(res_x_m), abs(res_y_m)


def test_resample_raster():
    resample_raster(INPUT_PATH, OUTPUT_PATH, TARGET_RESOLUTION_M)

    assert OUTPUT_PATH.exists()

    with rasterio.open(INPUT_PATH) as source, rasterio.open(OUTPUT_PATH) as dataset:
        assert dataset.crs == source.crs
        assert dataset.nodata == NODATA

        values = dataset.read(1)
        res_x_m, res_y_m = _pixel_resolution_m(dataset)

    assert values.size > 0
    assert np.any(values != NODATA)
    assert abs(res_x_m - TARGET_RESOLUTION_M) <= RESOLUTION_TOLERANCE_M
    assert abs(res_y_m - TARGET_RESOLUTION_M) <= RESOLUTION_TOLERANCE_M
