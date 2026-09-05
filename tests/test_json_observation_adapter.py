from adapters.json_observation_adapter import load_json_observations


def test_load_json_observations():
    observations = load_json_observations(
        "data/raw/mock_observations.json",
        source="mock-json",
        variable="rainfall",
    )

    assert len(observations) == 3

    first = observations[0]

    assert first["source"] == "mock-json"
    assert first["variable"] == "rainfall"
    assert first["value"] == 12.5
    assert first["unit"] == "mm"
    assert first["latitude"] == 13.0827
    assert first["longitude"] == 80.2707
    assert first["observed_at"] == "2024-09-01T06:00:00Z"
    assert first["received_at"] == "2024-09-01T06:05:00Z"
    assert first["quality_score"] == 1.0
