from pathlib import Path

import numpy as np
import rasterio

from preprocessing.spatial_aligner import align_raster_to_reference

NODATA = -9999.0

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "resampled_rainfall.tif"
REFERENCE_PATH = PROJECT_ROOT / "data" / "raw" / "mock_reference.tif"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "aligned_rainfall.tif"


def test_align_raster_to_reference():
    align_raster_to_reference(INPUT_PATH, REFERENCE_PATH, OUTPUT_PATH)

    assert OUTPUT_PATH.exists()

    with rasterio.open(REFERENCE_PATH) as reference, rasterio.open(
        OUTPUT_PATH
    ) as aligned:
        assert aligned.crs == reference.crs
        assert aligned.width == reference.width
        assert aligned.height == reference.height
        assert aligned.transform == reference.transform
        assert aligned.nodata == reference.nodata
        assert aligned.nodata == NODATA
        values = aligned.read(1)

    assert values.size > 0
    assert np.any(values != NODATA)
