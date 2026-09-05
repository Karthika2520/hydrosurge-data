from pathlib import Path
import re

import h5py
import numpy as np


def read_imerg_hdf5(file_path):
    """
    Read a NASA GPM IMERG half-hourly HDF5 rainfall file.

    Returns:
        dict containing precipitation, latitude, longitude and metadata.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"IMERG file not found: {file_path}")

    with h5py.File(file_path, "r") as hdf:

        required_datasets = [
            "Grid/precipitation",
            "Grid/lat",
            "Grid/lon",
        ]

        for dataset_name in required_datasets:
            if dataset_name not in hdf:
                raise KeyError(
                    f"Required dataset not found in IMERG file: {dataset_name}"
                )

        precipitation_dataset = hdf["Grid/precipitation"]
        precipitation = np.asarray(precipitation_dataset[:], dtype=np.float32)

        lat = np.asarray(hdf["Grid/lat"][:], dtype=np.float32)
        lon = np.asarray(hdf["Grid/lon"][:], dtype=np.float32)

        units = precipitation_dataset.attrs.get("units", b"mm/hr")

        if isinstance(units, bytes):
            units = units.decode("utf-8")

        # IMERG has one time slice in the half-hourly file.
        if precipitation.ndim == 3 and precipitation.shape[0] == 1:
            precipitation = precipitation[0]

        if precipitation.ndim != 2:
            raise ValueError(
                f"Expected a 2D precipitation grid after removing time dimension, "
                f"got shape {precipitation.shape}"
            )

        # Expected IMERG arrangement:
        # precipitation = (longitude, latitude)
        if precipitation.shape != (len(lon), len(lat)):
            raise ValueError(
                "Precipitation dimensions do not match longitude/latitude dimensions: "
                f"precipitation={precipitation.shape}, "
                f"lon={len(lon)}, lat={len(lat)}"
            )

        # Convert to raster orientation: (latitude, longitude)
        precipitation = precipitation.T

        # Replace IMERG fill value with NaN.
        precipitation[precipitation <= -9999.0] = np.nan

        observed_at = extract_timestamp_from_filename(file_path.name)

        return {
            "precipitation": precipitation,
            "lat": lat,
            "lon": lon,
            "unit": units,
            "source": "NASA GPM IMERG Final V07B",
            "variable": "precipitation",
            "observed_at": observed_at,
            "native_resolution": "0.1 degree x 0.1 degree",
            "crs": "EPSG:4326",
            "input_file": str(file_path),
            "nodata": -9999.0,
        }


def extract_timestamp_from_filename(filename):
    """
    Extract IMERG observation start time from a NASA IMERG filename.

    Example:
    ...20250901-S110000-E112959...
    -> 2025-09-01T11:00:00Z
    """

    match = re.search(r"(\d{8})-S(\d{6})-", filename)

    if not match:
        return None

    date_part = match.group(1)
    time_part = match.group(2)

    return (
        f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]}"
        f"T{time_part[:2]}:{time_part[2:4]}:{time_part[4:6]}Z"
    )