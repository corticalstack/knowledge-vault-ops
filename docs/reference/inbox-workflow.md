# Inbox Workflow

## Purpose

The inbox is the ingestion interface. Every new source enters the vault by being written to an inbox folder. From there, automation takes over.

## Three Inbox Types

| Inbox path | What goes in | Who reads it |
|---|---|---|
| `<Domain>/_inbox/` | New concepts, articles, papers | vault-ingest → creates or enriches wiki page |
| `projects/{repo}/_inbox/` | Repo-specific decisions, tradeoffs | vault-ingest → updates context.md or patterns.md |
| `agents-shared/_inbox/` | Cross-repo patterns, gotchas | vault-ingest → updates patterns.md or mistakes.md |

## Why Inbox, Not Direct Edit

1. Keeps the trigger surface clean: the Action fires on `*/_inbox/*.md` path patterns
2. Separates raw source from compiled wiki — the inbox file is deleted after ingestion; the citation lives in `## Sources` on the wiki page
3. Keeping raw source copies creates duplicate search results in Obsidian — inbox files are transient by design

## The Trigger Mechanism

The chain works as follows: drop a file into `_inbox/` locally in Obsidian → the Obsidian Git plugin auto-commits and pushes to GitHub → GitHub detects the push → the vault-ingest Action fires because the pushed path matches one of the `*/_inbox/*.md` patterns. The local→GitHub sync is the trigger mechanism — there is no polling or scheduled check; every push is evaluated against the path filter.

## Manual Usage from a Claude Code Session

Two patterns:

1. **Direct:** say "integrate new document AI/_inbox/my-topic.md" — Claude reads the file and processes it inline.
2. **Capture:** say "capture this to the vault" — Claude determines the right inbox (domain, per-repo, or agents-shared), writes a well-formed summary, commits, and pushes. vault-ingest fires automatically on the push.

From any repo, Claude will also proactively suggest capturing when it encounters a novel concept, a non-obvious tradeoff that took significant reasoning to resolve, or a bug root cause that isn't already documented in the vault. You can reply yes or no.

## Inbox File Format

See [templates/inbox-entry.md](../../templates/inbox-entry.md) for the canonical template. The format matters: vault-ingest reads the frontmatter to determine ingestion behaviour. Key fields:

- `sources` — list of URLs the content was drawn from
- `luminary` — the luminary who authored the content (null for manual captures)
- `date` — the date the source content was published (YYYY-MM-DD)
- `domain` — target vault domain (AI | Cloud | Data | Engineering | Homelab)
- `capture_type` — `new_concept` or `enrichment`
- `enriches` — `[[Page Name]]` if enrichment; omit for new concepts
- `origin` — `manual` or `luminary-scan`

The body requires four sections: `## Summary`, `## Key Points`, `## Connections`, and `## Source Quote / Key Excerpt`.
