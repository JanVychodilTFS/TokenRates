"""Fetch and parse OpenAI Work and Codex credit rates as JSON."""

from __future__ import annotations

import json
import re
import sys

import requests

RATE_CARD_URL = (
    "https://help.openai.com/en/articles"
    "/11481834-chatgpt-rate-card-business-enterpriseedu-credit-based-pricing"
)


def number(text: str) -> float | int:
    """Convert a cell such as '1,250 credits' to 1250."""
    match = re.search(r"[\d,]+(?:\.\d+)?", text)
    if not match:
        raise ValueError(f"Expected a number, got {text!r}")

    value = float(match.group().replace(",", ""))
    return int(value) if value.is_integer() else value


def parse_credit_rates(markdown: str) -> list[dict[str, float | int | str]]:
    """Extract the Work and Codex token-credit table from Markdown."""
    lines = markdown.splitlines()
    start = next(
        (
            index
            for index, line in enumerate(lines)
            if line.lstrip().startswith("|")
            and "model" in line.casefold()
            and "input tokens" in line.casefold()
            and "cached input tokens" in line.casefold()
            and "output tokens" in line.casefold()
        ),
        None,
    )
    if start is None:
        raise ValueError(
            "Could not find a four-column token-credit rate table. "
            "Expected input, cached-input, and output token columns."
        )

    rates = []
    for line in lines[start + 2 :]:
        if not line.lstrip().startswith("|"):
            break

        model, input_value, cached_input, output = (
            cell.strip().strip("*")
            for cell in line.strip().strip("|").split("|")
        )
        try:
            rates.append(
                {
                    "model": model,
                    "input_credits_per_mtok": number(input_value),
                    "cached_input_credits_per_mtok": number(cached_input),
                    "output_credits_per_mtok": number(output),
                }
            )
        except ValueError:
            continue

    if not rates:
        raise ValueError("The rate-card table contained no model rates.")
    return rates


def fetch_credit_rates(source_url: str | None = None) -> dict[str, object]:
    """Fetch Markdown from markdown.new and return JSON-ready rate data."""
    source_url = source_url or RATE_CARD_URL
    response = requests.get("https://markdown.new/" + source_url, timeout=30)
    response.raise_for_status()

    return {
        "source_url": source_url,
        "rate_card": "ChatGPT Work and Codex",
        "unit": "credits_per_1m_tokens",
        "rates": parse_credit_rates(response.text),
    }


if __name__ == "__main__":
    try:
        rates = fetch_credit_rates()
        print(json.dumps(rates, indent=2, ensure_ascii=False))
    except Exception as error:
        print(f"error: {type(error).__name__}: {error}", file=sys.stderr)
        raise SystemExit(1)
