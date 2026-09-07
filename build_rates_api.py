"""Build date-addressable static JSON rate endpoints from rate history."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path


HISTORY_DIR = Path(__file__).parent / "rate_history"
RATES_DIR = Path(__file__).parent / "rates"
HISTORY_DATE_FORMAT = "%d-%m-%Y"
API_DATE_FORMAT = "%Y-%m-%d"


def parse_history_date(value: object) -> datetime:
    """Parse a date stored in a rate-history file."""
    return datetime.strptime(str(value), HISTORY_DATE_FORMAT)


def api_period(period: dict[str, object], requested_date: datetime | None = None) -> dict[str, object]:
    """Convert one stored period to public API response format."""
    response: dict[str, object] = {
        "observed_from": parse_history_date(period["start"]).strftime(API_DATE_FORMAT),
        "observed_until": parse_history_date(period["until"]).strftime(API_DATE_FORMAT),
        "source_url": period["source_url"],
        "rate_card": period["rate_card"],
        "unit": period["unit"],
        "rates": period["rates"],
    }
    if requested_date is not None:
        response["requested_date"] = requested_date.strftime(API_DATE_FORMAT)
    return response


def load_periods() -> list[dict[str, object]]:
    """Load history files in chronological order."""
    periods = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in HISTORY_DIR.glob("*_to_*.json")
    ]
    return sorted(periods, key=lambda period: parse_history_date(period["start"]))


def write_json(path: Path, value: object) -> None:
    """Write formatted JSON, creating its parent directory when needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def build_rates_api() -> None:
    """Build rates/latest.json and rates/YYYY-MM-DD.json endpoints."""
    periods = load_periods()
    if not periods:
        raise ValueError("Rate history contains no period files.")

    if RATES_DIR.exists():
        shutil.rmtree(RATES_DIR)
    RATES_DIR.mkdir()
    (RATES_DIR / ".nojekyll").touch()

    for period in periods:
        current_date = parse_history_date(period["start"])
        until = parse_history_date(period["until"])
        while current_date <= until:
            write_json(
                RATES_DIR / f"{current_date.strftime(API_DATE_FORMAT)}.json",
                api_period(period, requested_date=current_date),
            )
            current_date += timedelta(days=1)

    write_json(RATES_DIR / "latest.json", api_period(periods[-1]))


if __name__ == "__main__":
    build_rates_api()
