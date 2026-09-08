# TokenRates

Static JSON history of OpenAI Work and Codex token-credit rates. The data is collected from the [OpenAI ChatGPT rate card](https://help.openai.com/en/articles/11481834-chatgpt-rate-card-business-enterpriseedu-credit-based-pricing), recorded by observation date, and published through GitHub Pages.

## API quick start

Base URL: <https://janvychodiltfs.github.io/TokenRates/>

- [Latest observed rate period](https://janvychodiltfs.github.io/TokenRates/latest.json)
- Rates for a calendar date: `/YYYY-MM-DD.json` — replace `YYYY-MM-DD` with a date, for example [`2026-08-21.json`](https://janvychodiltfs.github.io/TokenRates/2026-08-21.json)

`latest.json` returns the newest recorded period. A dated endpoint returns the rate period that includes the requested date. Dates outside recorded history do not have an endpoint.

Each response uses `credits_per_1m_tokens` and has this shape:

```json
{
  "observed_from": "2026-08-21",
  "observed_until": "2026-09-03",
  "requested_date": "2026-08-21",
  "source_url": "https://help.openai.com/en/articles/11481834-chatgpt-rate-card-business-enterpriseedu-credit-based-pricing",
  "rate_card": "ChatGPT Work and Codex",
  "unit": "credits_per_1m_tokens",
  "rates": [
    {
      "model": "GPT-5.6 Sol",
      "input_credits_per_mtok": 100,
      "cached_input_credits_per_mtok": 10,
      "output_credits_per_mtok": 500
    }
  ]
}
```

`requested_date` appears only in dated responses. `latest.json` omits it. `observed_from` and `observed_until` identify when this project observed the rate card, not a pricing guarantee from OpenAI.

## Automation and deployment

GitHub Actions runs daily at 00:00 UTC and can also run manually. It fetches current rates, commits changed `rate_history/` files, builds the `rates/` directory, then deploys that directory to GitHub Pages. The deployed artifact contains the JSON endpoints plus its small index page.

## Source and disclaimer

This project provides a date-addressable record of observed rates, not an official OpenAI pricing service or pricing advice. Values may be delayed, incomplete, or superseded. Use the linked [OpenAI rate card](https://help.openai.com/en/articles/11481834-chatgpt-rate-card-business-enterpriseedu-credit-based-pricing) as the authoritative source before making decisions.
