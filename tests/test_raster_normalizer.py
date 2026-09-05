from pathlib import Path

import numpy as np
import rasterio
from rasterio.crs import CRS

NODATA = -9999.0
EXPECTED_SHAPE = (5, 5)
EXPECTED_VALUES = np.array(
    [
        [12.5, 8.2, 21.7, 4.1, 15.9],
        [10.0, NODATA, 7.3, 18.4, 9.1],
        [5.5, 6.2, 11.0, 14.8, 3.3],
        [16.1, 2.4, 19.0, 8.8, 12.2],
        [7.7, 13.5, 4.6, 20.1, 1.2],
    ],
    dtype=np.float32,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
NORMALIZED_PATH = PROJECT_ROOT / "data" / "processed" / "normalized_rainfall.tif"


def test_normalized_rainfall_raster():
    assert NORMALIZED_PATH.exists()

    with rasterio.open(NORMALIZED_PATH) as dataset:
        assert dataset.crs == CRS.from_epsg(4326)
        assert dataset.width == 5
        assert dataset.height == 5
        assert dataset.nodata == NODATA

        values = dataset.read(1)

    assert values.shape == EXPECTED_SHAPE
    np.testing.assert_array_equal(values, EXPECTED_VALUES)
    assert np.any(values == NODATA)
