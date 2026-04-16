# Configuration

This page covers the decisions a replicator must personalise. Everything else can be copied verbatim from `templates/`.

## Domain Map

The default domain set is: **AI**, **Cloud**, **Data**, **Engineering**, **Homelab**.

If your vault uses different domains, update the following in sync:

1. **Top-level folder names** in your vault — the domain folders themselves.
2. **`vault-ingest.yml` trigger paths** — the `on.push.paths` list watches specific `_inbox/**` paths. Update each entry to match your domain names, e.g. replace `AI/_inbox/**` with your equivalent.
3. **`DOMAIN_MAP` in `add_frontmatter.py`** — this dict maps domain folder names to the `domain:` frontmatter value written into each note.
4. **Vault `CLAUDE.md` valid domain list** — the vault CLAUDE.md contains an explicit list of valid domains that vault-ingest uses when classifying inbox files. Add or remove domains to match.
5. **Run graphify** to discover your vault's natural clusters before committing to domain names — let the graph suggest labels rather than imposing an arbitrary structure. See [graphify](../reference/graphify.md) for details.

## Luminaries Roster

Start from `templates/luminaries.json`. Edit it to match your focus areas:

- **Remove** luminaries whose domains are outside your interests — each luminary adds scan time and cost.
- **Add** luminaries using the existing schema fields: `name`, `slug`, `twitter_handle`, `blog_url`, `focus`.
- The **`focus` field** is passed to Claude as context when classifying captured content — be specific. "distributed systems and database internals" is more useful than "engineering".
- Keep the file at `luminary-scan/luminaries.json` in your vault root. The Action reads it from that path.

## Cron Schedule

Default: `0 23 * * *` (23:00 UTC daily).

To change it, edit the `cron:` line in `luminary-scan.yml`:

```yaml
on:
  schedule:
    - cron: '0 23 * * *'   # change this
```

**Sizing note**: each luminary scan can take 1–3 minutes. At 43 luminaries, a full run can take up to 2 hours. The Action has `timeout-minutes: 60` set — adjust this upward if your roster is significantly larger, or downward if you want a hard cap on runtime. See [Costs](costs.md) for runner-minute implications.

## seen-urls.json

`luminary-scan` maintains a deduplication list so it does not re-ingest URLs it has already processed.

Initialise the file as an empty JSON array:

```json
[]
```

Place it at `luminary-scan/seen-urls.json` in your vault root. The Action reads and appends to this file after each luminary is processed. Commit the empty file before your first luminary-scan run — the Action will fail if the file is missing.
