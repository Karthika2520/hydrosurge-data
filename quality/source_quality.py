from quality.observation_quality import generate_observation_quality_report

# PROJECT HEURISTIC: weighted blend of existing quality indicators.
# This is not a calibrated scientific formula.
OVERALL_COMPLETENESS_WEIGHT = 0.30
OVERALL_RANGE_WEIGHT = 0.25
OVERALL_DUPLICATE_WEIGHT = 0.15
OVERALL_LATENCY_WEIGHT = 0.15
OVERALL_SOURCE_QUALITY_WEIGHT = 0.15
LATENCY_HALF_LIFE_SECONDS = 300.0


def _clamp_unit_interval(value):
    return max(0.0, min(1.0, value))


def _latency_score(average_latency_seconds):
    # PROJECT HEURISTIC: 0s -> 1.0, 300s -> 0.5, larger latency -> lower score.
    return _clamp_unit_interval(
        1.0 / (1.0 + average_latency_seconds / LATENCY_HALF_LIFE_SECONDS)
    )


def _fallback_state(overall_quality):
    if overall_quality >= 0.80:
        return "primary"
    if overall_quality >= 0.50:
        return "degraded"
    return "fallback"


def assess_source_quality(observations):
    """Return a downstream-consumable source quality assessment.

    overall_quality is a PROJECT HEURISTIC, not a calibrated scientific formula:

        overall_quality =
            0.30 * completeness
            + 0.25 * range_validity
            + 0.15 * (1 - duplicate_rate)
            + 0.15 * latency_score
            + 0.15 * source_quality_score

    latency_score is also a PROJECT HEURISTIC:

        latency_score = 1 / (1 + average_latency_seconds / 300)
    """
    report = generate_observation_quality_report(observations)
    latency_score = _latency_score(report["source_latency"]["average_seconds"])
    overall_quality = _clamp_unit_interval(
        OVERALL_COMPLETENESS_WEIGHT * report["completeness"]
        + OVERALL_RANGE_WEIGHT * report["range_validity"]
        + OVERALL_DUPLICATE_WEIGHT * (1.0 - report["duplicate_rate"])
        + OVERALL_LATENCY_WEIGHT * latency_score
        + OVERALL_SOURCE_QUALITY_WEIGHT * report["source_quality_score"]
    )

    return {
        "overall_quality_score": overall_quality,
        "latency_score": latency_score,
        "fallback_state": _fallback_state(overall_quality),
    }
