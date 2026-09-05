import pandas as pd

REQUIRED_COLUMNS = [
    "latitude",
    "longitude",
    "value",
    "unit",
    "observed_at",
    "received_at",
]


def load_csv_observations(file_path, source, variable, quality_score=1.0):
    dataframe = pd.read_csv(
        file_path,
        dtype={
            "unit": "string",
            "observed_at": "string",
            "received_at": "string",
        },
    )

    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in dataframe.columns
    ]
    if missing_columns:
        raise ValueError(
            "Missing required CSV columns: " + ", ".join(missing_columns)
        )

    observations = []
    for row_index, row in dataframe.iterrows():
        for column in REQUIRED_COLUMNS:
            if pd.isna(row[column]):
                raise ValueError(
                    f"Missing value for required column '{column}' in row {row_index}"
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
                "quality_score": quality_score,
            }
        )

    return observations
