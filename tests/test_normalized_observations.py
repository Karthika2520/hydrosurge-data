import json
from pathlib import Path

from jsonschema import Draft202012Validator

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
NORMALIZED_PATH = PROJECT_ROOT / "data" / "processed" / "normalized_observations.json"
SCHEMA_PATH = PROJECT_ROOT / "contracts" / "observation.schema.json"


def test_normalized_observations():
    observations = json.loads(NORMALIZED_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    assert observations is not None
    assert len(observations) == 5

    for observation in observations:
        assert set(observation.keys()) == ALLOWED_FIELDS
        validator.validate(observation)
        assert observation["source"] == "mock-csv"
        assert observation["variable"] == "rainfall"
        assert 0 <= observation["quality_score"] <= 1
