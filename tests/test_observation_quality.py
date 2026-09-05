from adapters.csv_observation_adapter import load_csv_observations
from quality.observation_quality import generate_observation_quality_report


def test_normal_observations():
    observations = load_csv_observations(
        "data/raw/mock_observations.csv",
        source="mock-csv",
        variable="rainfall",
        quality_score=1.0,
    )

    report = generate_observation_quality_report(observations)

    assert report["completeness"] == 1.0
    assert report["range_validity"] == 1.0
    assert report["duplicate_rate"] == 0.0
    assert report["source_latency"]["average_seconds"] == 240.0
    assert report["source_quality_score"] == 1.0
    assert report["fallback_state"] == "primary"


def test_missing_required_field():
    observations = [
        {
            "source": "mock",
            "variable": "rainfall",
            "value": 10.0,
            "unit": "mm",
            "latitude": 13.0,
            "longitude": 80.0,
            "observed_at": "2024-09-01T06:00:00Z",
            "received_at": "2024-09-01T06:05:00Z",
        }
    ]

    report = generate_observation_quality_report(observations)

    assert report["completeness"] == 0.0
    assert report["fallback_state"] == "fallback"


def test_invalid_coordinates():
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
            "quality_score": 1.0,
        }
    ]

    report = generate_observation_quality_report(observations)

    assert report["range_validity"] == 0.0
    assert report["fallback_state"] == "fallback"


def test_duplicate_rate():
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

    observations = [observation, observation.copy()]

    report = generate_observation_quality_report(observations)

    assert report["duplicate_rate"] == 0.5


def test_empty_observations():
    report = generate_observation_quality_report([])

    assert report["completeness"] == 0.0
    assert report["range_validity"] == 0.0
    assert report["duplicate_rate"] == 0.0
    assert report["source_latency"]["average_seconds"] == 0.0
    assert report["source_quality_score"] == 0.0
    assert report["fallback_state"] == "fallback"