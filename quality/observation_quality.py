from datetime import datetime, timezone
import math


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


def _is_complete(observation):
    return all(
        field in observation
        and observation[field] is not None
        and observation[field] != ""
        for field in REQUIRED_FIELDS
    )


def _is_range_valid(observation):
    try:
        latitude = float(observation["latitude"])
        longitude = float(observation["longitude"])
        value = float(observation["value"])
        quality_score = float(observation["quality_score"])

        return (
            -90 <= latitude <= 90
            and -180 <= longitude <= 180
            and math.isfinite(value)
            and 0 <= quality_score <= 1
        )
    except (KeyError, TypeError, ValueError):
        return False


def _parse_timestamp(timestamp):
    value = str(timestamp)

    if value.endswith("Z"):
        value = value[:-1] + "+00:00"

    parsed = datetime.fromisoformat(value)

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed


def generate_observation_quality_report(observations):
    total = len(observations)

    if total == 0:
        return {
            "completeness": 0.0,
            "range_validity": 0.0,
            "duplicate_rate": 0.0,
            "source_latency": {
                "average_seconds": 0.0
            },
            "source_quality_score": 0.0,
            "fallback_state": "fallback",
        }

    complete_count = sum(
        1 for observation in observations if _is_complete(observation)
    )

    valid_range_count = sum(
        1 for observation in observations if _is_range_valid(observation)
    )

    completeness = complete_count / total
    range_validity = valid_range_count / total

    keys = []
    for observation in observations:
        key = (
            observation.get("source"),
            observation.get("variable"),
            observation.get("latitude"),
            observation.get("longitude"),
            observation.get("observed_at"),
        )
        keys.append(key)

    duplicate_count = total - len(set(keys))
    duplicate_rate = duplicate_count / total

    latencies = []

    for observation in observations:
        try:
            observed = _parse_timestamp(observation["observed_at"])
            received = _parse_timestamp(observation["received_at"])
            latency = (received - observed).total_seconds()
            latencies.append(latency)
        except (KeyError, TypeError, ValueError):
            continue

    average_latency = (
        sum(latencies) / len(latencies)
        if latencies
        else 0.0
    )

    quality_scores = []

    for observation in observations:
        try:
            quality_scores.append(float(observation["quality_score"]))
        except (KeyError, TypeError, ValueError):
            continue

    average_quality = (
        sum(quality_scores) / len(quality_scores)
        if quality_scores
        else 0.0
    )

    fallback_state = (
        "primary"
        if complete_count == total and valid_range_count == total
        else "fallback"
    )

    return {
        "completeness": completeness,
        "range_validity": range_validity,
        "duplicate_rate": duplicate_rate,
        "source_latency": {
            "average_seconds": average_latency
        },
        "source_quality_score": average_quality,
        "fallback_state": fallback_state,
    }