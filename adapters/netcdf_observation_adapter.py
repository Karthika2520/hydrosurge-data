from pathlib import Path

import pandas as pd
import xarray as xr


def load_netcdf_observations(
    file_path,
    source,
    variable="rainfall",
    quality_score=1.0,
):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"NetCDF file not found: {file_path}")

    dataset = xr.open_dataset(file_path)

    try:
        if variable not in dataset.data_vars:
            raise KeyError(
                f"Variable '{variable}' not found in NetCDF file"
            )

        required_coordinates = ["time", "latitude", "longitude"]

        for coordinate in required_coordinates:
            if coordinate not in dataset:
                raise KeyError(
                    f"Required coordinate '{coordinate}' not found"
                )

        values = dataset[variable].values
        times = dataset["time"].values
        latitudes = dataset["latitude"].values
        longitudes = dataset["longitude"].values

        if not (
            len(values)
            == len(times)
            == len(latitudes)
            == len(longitudes)
        ):
            raise ValueError(
                "NetCDF time, latitude, longitude and variable lengths must match"
            )

        unit = dataset[variable].attrs.get("units", "")

        observations = []

        for index in range(len(values)):
            timestamp = pd.Timestamp(times[index])

            observed_at = (
                timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
            )

            observations.append(
                {
                    "source": source,
                    "variable": variable,
                    "value": float(values[index]),
                    "unit": str(unit),
                    "latitude": float(latitudes[index]),
                    "longitude": float(longitudes[index]),
                    "observed_at": observed_at,
                    "received_at": observed_at,
                    "quality_score": float(quality_score),
                }
            )

        return observations

    finally:
        dataset.close()
