# Costs

## Claude Code Subscription

Both Actions invoke `claude -p` authenticated via a Claude Code OAuth token. If you have a Claude Code subscription, Action runs are covered — there is no additional per-token API cost. This is the approach used in this system and the reason `CLAUDE_CODE_OAUTH_TOKEN` is the required secret rather than a raw API key.

## Raw API Key Alternative

If you do not have a Claude Code subscription, you can replace `claude -p` with direct Anthropic API calls in the workflow scripts. Rough estimates at current pricing:

- **vault-ingest, single inbox file**: ~$0.01–$0.05 per run, depending on page complexity and the model used.
- **luminary-scan with 43 luminaries**: ~$1–$3 per nightly run, depending on how much new content is found and processed.

At those rates, a heavily used vault (active daily ingest plus nightly luminary scan) would cost roughly $30–$100/month on raw API. A Claude Code subscription is more economical if you are already using the CLI for other work.

## GitHub Actions Runner Minutes

Both Actions run on `ubuntu-latest` (GitHub-hosted runners). The free tier includes 2,000 minutes per month for public repositories; private repositories have the same 2,000-minute allowance on the free plan.

Typical runtimes:

- **vault-ingest**: 2–5 minutes per run (one inbox file processed per trigger).
- **luminary-scan**: up to 60 minutes per run (the workflow has `timeout-minutes: 60`).

For a vault with active daily use — 1–2 inbox drops per day plus one nightly luminary scan — the monthly total is approximately 90–120 minutes. This is well within the free tier.

If you expand the luminaries roster significantly or trigger vault-ingest many times per day, recalculate against the 2,000-minute limit.

## Storage

The vault grows continuously as wiki pages are added and `seen-urls.json` accumulates processed URLs. No special storage management is needed. GitHub's soft limit for repository size is 1 GB — a text-only vault with hundreds of wiki pages will be well under this limit for years of normal operation.
