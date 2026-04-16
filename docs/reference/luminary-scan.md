# luminary-scan GitHub Action

## Overview

The luminary-scan Action runs nightly and searches for content authored by 43 tracked luminaries across six sources: X/Twitter, personal blogs, Hacker News, arXiv, Papers With Code, and HuggingFace. Only content the luminary wrote themselves, published yesterday, and that passes a novelty filter is captured. Passing content is written to the appropriate domain inbox (`AI/_inbox/`, `Cloud/_inbox/`, etc.) where vault-ingest picks it up on the next push. The key design goal is to automate frontier knowledge capture without ingesting noise or re-ingesting content the vault already covers well.

## Schedule

Cron: `0 23 * * *` — 23:00 UTC, which is midnight CET (UTC+1).

The Action also fires on `workflow_dispatch`, allowing manual runs for testing or backfill purposes.

## Full YAML

```yaml
name: Luminary Scan

on:
  schedule:
    - cron: '0 23 * * *'   # 23:00 UTC = midnight CET (UTC+1)
  workflow_dispatch:         # manual trigger for testing

permissions:
  contents: write

env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true

jobs:
  scan:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    if: github.actor != 'github-actions[bot]'

    steps:
      - name: Checkout
        uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4
        with:
          token: ${{ secrets.VAULT_PAT }}

      - name: Configure git identity
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Set date variables
        run: |
          echo "SCAN_TODAY=$(date +%Y-%m-%d)" >> $GITHUB_ENV
          echo "SCAN_YESTERDAY=$(date -d 'yesterday' +%Y-%m-%d)" >> $GITHUB_ENV

      - name: Install Claude Code CLI
        run: npm install -g @anthropic-ai/claude-code

      - name: Run luminary scan
        env:
          CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
        run: |
          claude -p "
          You are running the nightly luminary scan for the knowledge vault.
          Today is $SCAN_TODAY. Yesterday was $SCAN_YESTERDAY.

          SETUP:
          1. Read luminary-scan/luminaries.json — this is your list of luminaries.
          2. Read luminary-scan/seen-urls.json — these are URLs already ingested; do not re-ingest them.

          FOR EACH LUMINARY in the list, in order, do all of the following:

          --- SEARCH ---
          Find content AUTHORED BY this luminary and published on $SCAN_YESTERDAY.
          Only capture content this person wrote themselves — not articles about them, not
          content that merely mentions them. Search across:
          - X/Twitter: search 'site:x.com/{twitter_handle} $SCAN_YESTERDAY' or 'from:{twitter_handle} since:$SCAN_YESTERDAY'
          - Blog: if blog_url is not null, fetch that URL and look for posts dated $SCAN_YESTERDAY
          - Hacker News: search '{name} site:news.ycombinator.com $SCAN_YESTERDAY' — only keep items with a visible score of 200 or more
          - arXiv: search '{name} arxiv $SCAN_YESTERDAY'
          - Papers With Code: check for papers by this person trending on $SCAN_YESTERDAY
          - Hugging Face blog: search for posts by or about this person dated $SCAN_YESTERDAY

          --- FILTER ---
          For each result URL:
          - Skip if the URL is already in seen-urls.json
          - Skip if you cannot confirm the content was published on or after $SCAN_YESTERDAY
          - Skip if it is a repost, retweet of someone else, pure product announcement, or marketing copy

          --- JUDGE NOVELTY ---
          For each candidate that passed the filter, extract the key concept or idea, then run:
            grep -ril '<concept-keywords>' . --include='*.md' | grep -v '_inbox\|\.github\|docs/superpowers\|luminary-scan' | head -10
          Interpret the results:
          - 3 or more strong matches: skip — already well-covered in the vault
          - 1-2 partial matches: enrichment candidate — note which existing page(s) to enrich
          - 0 matches: new concept candidate

          --- CAPTURE ---
          If the concept clears the signal threshold, do all of these steps:

          a. Determine the vault domain:
             AI       — ML concepts, models, research techniques, AI tools, prompting methods
             Cloud    — infrastructure, platforms, cloud services, deployment patterns
             Data     — data engineering, pipelines, analytics, databases
             Engineering — software practices, tooling, architecture patterns, developer workflows
             Homelab  — hardware, self-hosting, home infrastructure

          b. Research the concept: expand on what makes it novel, how it contrasts with existing vault
             content, and which existing vault pages it connects to.

          c. Write the inbox file to {Domain}/_inbox/$SCAN_YESTERDAY-{slug}-{concept-slug}.md
             where {slug} is the luminary's slug field from luminaries.json.

             Use EXACTLY this format for the inbox file (include the # title line and all sections):

          # {Concept Title}

          sources:
          - {primary URL — the post/tweet that triggered the capture}
          - {any additional URLs followed during research, e.g. linked blog post, arXiv paper, HN thread}
          luminary: {Full Name}
          date: $SCAN_YESTERDAY
          domain: {AI|Cloud|Data|Engineering|Homelab}
          capture_type: {new_concept|enrichment}
          enriches: [[Page Name]]
          origin: luminary-scan

          ## Summary

          {2-3 sentences capturing the core idea in plain language}

          ## Key Points

          - {key point}
          - {key point}
          - {key point}

          ## Connections

          - [[Existing Vault Page]] — {brief reason for the connection}

          ## Source Quote / Key Excerpt

          > {Direct quote or close paraphrase from the original source}

          Note: if capture_type is new_concept, omit the 'enriches:' line entirely.

          --- AFTER EACH LUMINARY (always do this, even if nothing was captured) ---
          1. Read luminary-scan/seen-urls.json
          2. Append all source URLs from the inbox file's sources: list to the JSON array
          3. Write the updated array back to luminary-scan/seen-urls.json
          4. Stage ONLY the current luminary's files and seen-urls.json — never use git add -A:
               git add luminary-scan/seen-urls.json
               git add AI/_inbox/$SCAN_YESTERDAY-{slug}-*.md Cloud/_inbox/$SCAN_YESTERDAY-{slug}-*.md Data/_inbox/$SCAN_YESTERDAY-{slug}-*.md Engineering/_inbox/$SCAN_YESTERDAY-{slug}-*.md Homelab/_inbox/$SCAN_YESTERDAY-{slug}-*.md 2>/dev/null || true
               git commit -m 'scan({slug}): {one-line summary of what was captured, or \"no signal\"}'
          5. Push immediately so vault-ingest can pick up this luminary's inbox file:
               git pull --rebase origin main
               git push

          When all luminaries in the list have been processed: stop. Do not do anything else.
          " --dangerously-skip-permissions

      # Safety net: Claude pushes after each luminary within the session so vault-ingest
      # (which uses HEAD~1 diff) picks up each luminary's inbox files individually.
      # This step catches any commits Claude couldn't push due to transient errors.
      - name: Push any remaining commits
        run: |
          git pull --rebase origin main
          git push
```

## What the Claude Prompt Instructs

For each luminary, Claude executes the following steps in order:

1. **Setup** — Read `luminary-scan/luminaries.json` for the full list of luminaries and `luminary-scan/seen-urls.json` for the set of URLs already ingested. These two files are the scan's state.

2. **Search** — Search for content authored by the luminary and published yesterday across six sources: X/Twitter (using `from:{handle} since:{date}` or `site:x.com/{handle}`), the luminary's blog (if `blog_url` is not null), Hacker News (items with score ≥ 200), arXiv, Papers With Code, and HuggingFace. Content must be written by the luminary — not about them.

3. **Filter** — For each result URL: skip if already present in `seen-urls.json`; skip if the publication date cannot be confirmed as yesterday; skip if the content is a repost, retweet, pure product announcement, or marketing copy.

4. **Judge novelty** — Extract the key concept from the candidate, then run `grep -ril '<concept-keywords>' . --include='*.md'` against the vault (excluding `_inbox`, `.github`, `docs/superpowers`, and `luminary-scan` paths). Interpret: 3+ strong matches = skip (already well-covered); 1–2 partial matches = enrichment candidate (note which pages to enrich); 0 matches = new concept candidate.

5. **Capture** — If signal threshold is cleared: determine the vault domain (AI, Cloud, Data, Engineering, or Homelab), research the concept in depth, and write an inbox file to `{Domain}/_inbox/YYYY-MM-DD-{luminary-slug}-{concept-slug}.md` using the prescribed frontmatter and section format.

6. **After each luminary** — Read `seen-urls.json`, append all captured source URLs, write it back, stage only that luminary's inbox files and `seen-urls.json` (never `git add -A`), commit with message `scan({slug}): {summary or "no signal"}`, then immediately `git pull --rebase` and `git push`.

## Novelty Filter Design

The scan applies four filters before writing any inbox file:

**Authorship filter** — Content must be authored by the luminary, not merely about them. An article citing Andrej Karpathy is not captured; a tweet or blog post written by Andrej Karpathy is. This prevents the vault from accumulating secondary commentary on influential people rather than the ideas themselves.

**Date filter** — Content must have been published yesterday. Old content resurfaces constantly via aggregators, newsletters, and retweets. Anchoring on a 24-hour window prevents known content from re-entering the pipeline just because it recirculated.

**HN score threshold (≥ 200)** — Hacker News search returns a broad mix of engagement levels. Requiring a visible score of at least 200 filters out low-engagement posts that rarely represent a genuinely novel idea gaining traction. Posts scoring below this threshold are dropped regardless of authorship or date.

**Grep-before-capture** — Before writing an inbox file, Claude greps the existing vault for the concept's keywords. Three or more strong matches across existing wiki pages means the vault already covers the topic well and re-ingesting it adds noise rather than knowledge. This is the final gate between the search results and the inbox.

## Per-Luminary Push Cadence

Each luminary's results are committed and pushed immediately after processing — not accumulated into a single batch push at the end of the scan.

The reason is the downstream cascade. vault-ingest is triggered by pushes that touch inbox paths. It uses `find` to locate all inbox files currently present in the repository (not a git diff) — anything that exists at `*/_inbox/*.md` is processed and then deleted, so accumulation is not an issue. However, if all 43 luminaries committed at once and pushed once, vault-ingest would need to process up to 43 inbox files in a single triggered run, which risks timing out and produces a single opaque commit attributing the entire capture batch to one push event.

Per-luminary push means:

- vault-ingest processes each luminary's inbox file in its own triggered run, independently and with a clean scope.
- If vault-ingest fails or times out on one luminary's content, it does not affect the others.
- The commit history directly attributes each capture to the specific luminary whose content triggered it (`scan(karpathy): ...`, `scan(lecun): ...`, etc.), making the audit trail readable.

The "Push any remaining commits" step at the end of the Action is a safety net for any commits Claude produced but could not push due to transient network errors during the scan session.

## luminaries.json Schema

Each entry in `luminaries.json` has the following shape:

```json
{
  "name": "Full Name",
  "slug": "url-safe-slug",
  "twitter_handle": "handle_without_at",
  "blog_url": "https://... or null",
  "focus": "brief description of their domain focus"
}
```

Field notes:

- `slug` is used in inbox filenames (`YYYY-MM-DD-{slug}-{concept-slug}.md`) and in commit messages (`scan({slug}): ...`). It must be URL-safe (lowercase, hyphens only).
- `twitter_handle` is without the `@` prefix. Used directly in search queries.
- `blog_url` can be `null`. When null, the scan still covers X/Twitter, HN, arXiv, Papers With Code, and HuggingFace for that person.
- `focus` is used by Claude to calibrate which vault domain the content maps to and to weight search results. It should be specific — "neural nets, LLM tooling, engineering practice" gives Claude more signal than "AI researcher". Vague focus fields produce less accurate domain assignments.

The full list of 43 luminaries is in `templates/luminaries.json` in this repository. That file is the source of truth for bootstrapping a new vault or resetting the luminary list.

## Guard Condition

```yaml
if: github.actor != 'github-actions[bot]'
```

This condition prevents luminary-scan from re-triggering on its own pushes. When Claude commits and pushes per-luminary results, the actor on those pushes is `github-actions[bot]`. Without this guard, each push would trigger a new scan run, creating an infinite loop.

**Contrast with vault-ingest's guard mechanism.** vault-ingest uses a commit-message-based guard — `!startsWith(github.event.head_commit.message, 'ingest:')` — it skips processing when the triggering commit message starts with `ingest:`. It cannot use an actor-based guard because it needs to process pushes made by `github-actions[bot]` — those are exactly the per-luminary pushes from luminary-scan that carry inbox files.

The two guards are deliberately different and complementary:

| Action | Guard type | Allows through | Blocks |
|---|---|---|---|
| luminary-scan | Actor-based (`github.actor != 'github-actions[bot]'`) | Human pushes, `workflow_dispatch` | Bot's own per-luminary pushes |
| vault-ingest | Commit-message-based (`!startsWith(msg, 'ingest:')`) | Bot pushes with `scan(...)` commits | Bot's own `ingest:` wiki-update commits |

This asymmetry is required: luminary-scan pushes under the `github-actions[bot]` identity and must trigger vault-ingest; vault-ingest must not re-trigger itself on its own wiki commits.

## Required Secrets

Two secrets must be configured in the vault repository's GitHub Actions secrets:

**`CLAUDE_CODE_OAUTH_TOKEN`** — OAuth token for the Claude Code CLI. Used by the `Run luminary scan` step to authenticate `claude -p` invocations. Without this, the scan step will fail to call Claude.

**`VAULT_PAT`** — GitHub Personal Access Token with `contents: write` scope. Used in the `Checkout` step (`token: ${{ secrets.VAULT_PAT }}`).

Why `VAULT_PAT` and not the default `GITHUB_TOKEN`: `GITHUB_TOKEN` does not trigger further workflow runs. GitHub deliberately restricts it this way to prevent accidental Action cascades. Each per-luminary push from luminary-scan must trigger vault-ingest downstream — that cascade is the entire point of the per-luminary push cadence. A PAT authenticates as the token owner and does trigger further workflows. Using `GITHUB_TOKEN` here would silently break the cascade: luminary-scan would complete, pushes would land, but vault-ingest would never fire. This is the single most critical secret configuration detail in the system.
