import json
import re
from datetime import datetime
from pathlib import Path

from preprocessing.temporal_normalizer import normalize_observation_times

REQUIRED_FIELDS = {
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

UTC_Z_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$"
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "normalized_observations.json"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "temporal_normalized_observations.json"


def _assert_iso8601_utc(value):
    assert isinstance(value, str)
    assert UTC_Z_PATTERN.match(value)
    parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    assert parsed.tzinfo is not None
    assert parsed.utcoffset().total_seconds() == 0


def test_normalize_observation_times():
    original = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    normalize_observation_times(INPUT_PATH, OUTPUT_PATH)

    assert OUTPUT_PATH.exists()
    observations = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))

    assert observations
    assert len(observations) == len(original)

    original_by_key = {
        (item["latitude"], item["longitude"], item["value"]): item
        for item in original
    }
    observed_at_values = []

    for observation in observations:
        assert REQUIRED_FIELDS.issubset(observation.keys())
        _assert_iso8601_utc(observation["observed_at"])
        _assert_iso8601_utc(observation["received_at"])
        assert observation["observed_at"] <= observation["received_at"]
        observed_at_values.append(observation["observed_at"])

        key = (observation["latitude"], observation["longitude"], observation["value"])
        source_observation = original_by_key[key]
        assert observation["value"] == source_observation["value"]
        assert observation["latitude"] == source_observation["latitude"]
        assert observation["longitude"] == source_observation["longitude"]
        assert observation["quality_score"] == source_observation["quality_score"]

    assert observed_at_values == sorted(observed_at_values)
