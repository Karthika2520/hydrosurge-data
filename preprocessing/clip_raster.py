from pathlib import Path

import rasterio
from rasterio.windows import from_bounds


def clip_raster(
    input_path,
    output_path,
    west=80.15,
    south=12.90,
    east=80.35,
    north=13.20,
):
    input_path = Path(input_path)
    output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(input_path) as src:

        window = from_bounds(
            west,
            south,
            east,
            north,
            src.transform,
        )

        window = window.round_offsets().round_lengths()

        data = src.read(1, window=window)

        transform = src.window_transform(window)

        profile = src.profile.copy()

        profile.update(
            {
                "height": data.shape[0],
                "width": data.shape[1],
                "transform": transform,
                "nodata": -9999.0,
                "dtype": "float32",
            }
        )

        with rasterio.open(output_path, "w", **profile) as dst:
            dst.write(data.astype("float32"), 1)
            dst.update_tags(**src.tags())

            dst.update_tags(
                pilot_area="Chennai",
                clip_bounds=f"{west},{south},{east},{north}",
            )

    return output_path