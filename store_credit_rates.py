"""Store one JSON file for each distinct observed credit-rate period."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from parse_credit_rates import fetch_credit_rates


HISTORY_DIR = Path(__file__).parent / "rate_history"


def today() -> str:
    """Return the current UTC date as DD-MM-YYYY."""
    return datetime.now(UTC).strftime("%d-%m-%Y")


def filename_time(value: str) -> str:
    """Validate and return a date-only period value."""
    datetime.strptime(value, "%d-%m-%Y")
    return value


def date_value(value: str) -> datetime:
    """Parse a date-only period value for chronological comparisons."""
    return datetime.strptime(value, "%d-%m-%Y")


def rate_hash(rate_data: dict[str, object]) -> str:
    """Create a stable hash from rates, excluding observed-time metadata."""
    rate_json = json.dumps(
        rate_data["rates"],
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(rate_json.encode()).hexdigest()


def history_file(start: str, until: str, suffix: str = "") -> Path:
    """Return the filename for one observed rate period."""
    period_number = 1 + sum(
        date_value(str(load_json(path)["start"])) < date_value(start)
        for path in HISTORY_DIR.glob("*_to_*.json")
    )
    name = (
        f"{period_number}_{filename_time(start)}_to_"
        f"{filename_time(until)}{suffix}.json"
    )
    return HISTORY_DIR / name


def latest_history_file() -> Path | None:
    """Return the most recently observed rate-period file, if it exists."""
    files = list(HISTORY_DIR.glob("*_to_*.json"))
    return max(
        files,
        key=lambda file: date_value(str(load_json(file)["until"])),
        default=None,
    )


def load_json(path: Path) -> dict[str, object]:
    """Load one stored rate-period file."""
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, object]) -> None:
    """Write formatted JSON to a rate-period file."""
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def store_rate_data(
    rate_data: dict[str, object],
    start: str,
    until: str,
) -> Path:
    """Store already-parsed rates for an explicit observed period."""
    if date_value(start) > date_value(until):
        raise ValueError("The start time must be earlier than the until time.")

    HISTORY_DIR.mkdir(exist_ok=True)
    rate_data = dict(rate_data)
    rate_data["rate_hash"] = rate_hash(rate_data)
    rate_data["start"] = start
    rate_data["until"] = until

    rate_file = history_file(start, until)
    if rate_file.exists():
        existing = load_json(rate_file)
        if existing.get("rate_hash") != rate_data["rate_hash"]:
            rate_file = history_file(
                start,
                until,
                suffix=f"_{str(rate_data['rate_hash'])[:8]}",
            )

    write_json(rate_file, rate_data)
    return rate_file


def store_rate_period(source_url: str, start: str, until: str) -> Path:
    """Fetch one source URL and store it for an explicit observed period."""
    return store_rate_data(fetch_credit_rates(source_url), start, until)


def store_credit_rates() -> Path:
    """Fetch rates, extend the current period, or start a new one."""
    HISTORY_DIR.mkdir(exist_ok=True)
    current = fetch_credit_rates()
    current["rate_hash"] = rate_hash(current)
    checked_at = today()
    latest_file = latest_history_file()

    if latest_file is not None:
        latest = load_json(latest_file)
        if latest.get("rate_hash") == current["rate_hash"]:
            latest["until"] = checked_at
            updated_file = history_file(str(latest["start"]), checked_at)
            write_json(updated_file, latest)
            if updated_file != latest_file:
                latest_file.unlink()
            return updated_file

    current["start"] = checked_at
    current["until"] = checked_at
    new_file = history_file(checked_at, checked_at)
    if new_file.exists():
        new_file = history_file(
            checked_at,
            checked_at,
            suffix=f"_{str(current['rate_hash'])[:8]}",
        )
    write_json(new_file, current)
    return new_file


if __name__ == "__main__":
    print(store_credit_rates())
