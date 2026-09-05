import json
from datetime import datetime, timezone
from pathlib import Path


def _parse_aware_timestamp(value, field_name):
    if value is None or (isinstance(value, str) and value.strip() == ""):
        raise ValueError(f"Missing timestamp for '{field_name}'")
    if not isinstance(value, str):
        raise ValueError(f"Timestamp for '{field_name}' must be a string")

    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"Invalid timestamp for '{field_name}': {value}") from exc

    if parsed.tzinfo is None:
        raise ValueError(f"Timestamp for '{field_name}' is not timezone-aware")

    return parsed


def _to_utc_z(parsed):
    utc = parsed.astimezone(timezone.utc)
    iso_text = utc.isoformat()
    if iso_text.endswith("+00:00"):
        return iso_text[:-6] + "Z"
    raise ValueError("Failed to normalize timestamp to UTC Z format")


def normalize_observation_times(input_path, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    observations = json.loads(Path(input_path).read_text(encoding="utf-8"))
    normalized = []

    for observation in observations:
        observed_at = _parse_aware_timestamp(
            observation.get("observed_at"), "observed_at"
        )
        received_at = _parse_aware_timestamp(
            observation.get("received_at"), "received_at"
        )

        updated = dict(observation)
        updated["observed_at"] = _to_utc_z(observed_at)
        updated["received_at"] = _to_utc_z(received_at)
        normalized.append(updated)

    normalized.sort(key=lambda item: item["observed_at"])

    output_path.write_text(
        json.dumps(normalized, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
