import json
from pathlib import Path

from quality.source_quality import assess_source_quality

PROJECT_ROOT = Path(__file__).resolve().parents[1]
NORMALIZED_PATH = PROJECT_ROOT / "data" / "processed" / "normalized_observations.json"


def _observation(**overrides):
    observation = {
        "source": "mock",
        "variable": "rainfall",
        "value": 10.0,
        "unit": "mm",
        "latitude": 13.0,
        "longitude": 80.0,
        "observed_at": "2024-09-01T06:00:00Z",
        "received_at": "2024-09-01T06:05:00Z",
        "quality_score": 1.0,
    }
    observation.update(overrides)
    return observation


def _assert_valid_assessment(assessment):
    assert set(assessment.keys()) == {
        "overall_quality_score",
        "latency_score",
        "fallback_state",
    }
    assert 0.0 <= assessment["overall_quality_score"] <= 1.0
    assert 0.0 <= assessment["latency_score"] <= 1.0
    assert assessment["fallback_state"] in {"primary", "degraded", "fallback"}


def test_high_quality_observations_are_primary():
    observations = json.loads(NORMALIZED_PATH.read_text(encoding="utf-8"))
    assessment = assess_source_quality(observations)

    _assert_valid_assessment(assessment)
    assert assessment["fallback_state"] == "primary"
    assert assessment["overall_quality_score"] >= 0.80


def test_medium_quality_observations_are_degraded():
    observations = [
        _observation(
            quality_score=0.0,
            received_at="2024-09-01T07:00:00Z",
        )
    ]
    assessment = assess_source_quality(observations)

    _assert_valid_assessment(assessment)
    assert assessment["fallback_state"] == "degraded"
    assert 0.50 <= assessment["overall_quality_score"] < 0.80


def test_low_quality_observations_are_fallback():
    observations = [
        {
            "source": "mock",
            "variable": "rainfall",
            "value": 10.0,
            "unit": "mm",
            "latitude": 100.0,
            "longitude": 80.0,
            "observed_at": "2024-09-01T06:00:00Z",
            "received_at": "2024-09-01T06:05:00Z",
        }
    ]
    assessment = assess_source_quality(observations)

    _assert_valid_assessment(assessment)
    assert assessment["fallback_state"] == "fallback"
    assert assessment["overall_quality_score"] < 0.50


def test_empty_observations_are_fallback():
    assessment = assess_source_quality([])

    _assert_valid_assessment(assessment)
    assert assessment["fallback_state"] == "fallback"
    assert 0.0 <= assessment["overall_quality_score"] <= 1.0


def test_scores_stay_between_zero_and_one():
    cases = [
        json.loads(NORMALIZED_PATH.read_text(encoding="utf-8")),
        [_observation(quality_score=0.0, received_at="2024-09-01T07:00:00Z")],
        [{"latitude": 100.0, "longitude": 80.0}],
        [],
    ]

    for observations in cases:
        assessment = assess_source_quality(observations)
        _assert_valid_assessment(assessment)


def test_assessment_is_deterministic():
    observations = json.loads(NORMALIZED_PATH.read_text(encoding="utf-8"))
    first = assess_source_quality(observations)
    second = assess_source_quality(observations)

    assert first == second
