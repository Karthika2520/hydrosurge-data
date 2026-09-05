import json
from pathlib import Path


REQUIRED_FIELDS = [
    "latitude",
    "longitude",
    "value",
    "unit",
    "observed_at",
    "received_at",
]


def load_json_observations(file_path, source, variable, quality_score=1.0):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, dict):
        if "observations" not in data:
            raise ValueError(
                "JSON object must contain an 'observations' field"
            )
        observations_data = data["observations"]

    elif isinstance(data, list):
        observations_data = data

    else:
        raise ValueError(
            "JSON must contain either an array of observations "
            "or an object with an 'observations' field"
        )

    if not isinstance(observations_data, list):
        raise ValueError("'observations' must be a list")

    observations = []

    for row_index, row in enumerate(observations_data):
        if not isinstance(row, dict):
            raise ValueError(
                f"Observation at index {row_index} must be an object"
            )

        missing_fields = [
            field for field in REQUIRED_FIELDS
            if field not in row
        ]

        if missing_fields:
            raise ValueError(
                f"Missing required JSON fields in row {row_index}: "
                + ", ".join(missing_fields)
            )

        for field in REQUIRED_FIELDS:
            if row[field] is None:
                raise ValueError(
                    f"Missing value for required field "
                    f"'{field}' in row {row_index}"
                )

        observations.append(
            {
                "source": source,
                "variable": variable,
                "value": float(row["value"]),
                "unit": str(row["unit"]),
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "observed_at": str(row["observed_at"]),
                "received_at": str(row["received_at"]),
                "quality_score": float(quality_score),
            }
        )

    return observations
