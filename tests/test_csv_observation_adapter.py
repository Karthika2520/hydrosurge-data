from pathlib import Path

from adapters.csv_observation_adapter import load_csv_observations

ALLOWED_FIELDS = {
    "source",
    "variable",
    "value",
    "unit",
    "latitude",
    "longitude",
    "observed_at",
    "received_at",
    "quality_score",
}

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = PROJECT_ROOT / "data" / "raw" / "mock_observations.csv"
SOURCE = "mock-csv"
VARIABLE = "rainfall"


def test_load_csv_observations():
    observations = load_csv_observations(
        CSV_PATH,
        source=SOURCE,
        variable=VARIABLE,
        quality_score=1.0,
    )

    assert observations is not None
    assert len(observations) == 5

    for observation in observations:
        assert set(observation.keys()) == ALLOWED_FIELDS
        assert observation["source"] == SOURCE
        assert observation["variable"] == VARIABLE
        assert 0 <= observation["quality_score"] <= 1
