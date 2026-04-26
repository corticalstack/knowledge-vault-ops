# References

Persistent, full-fidelity knowledge assets — hand-authored, never ingested, never rewritten.

## What lives here

- Extensive notes on systems architectures
- Exam / certification study material
- Long-form guides, playbooks, runbooks
- Any markdown where the document itself is the deliverable, not capture-material for the wiki

## What does NOT live here

- Short captures of a new concept → `Domain/_inbox/` (gets compiled into a wiki page)
- Per-repo architectural decisions → `projects/{repo}/_inbox/`
- Cross-repo patterns / gotchas → `agents-shared/_inbox/`

If you are unsure whether a note belongs here or in `_inbox/`, ask: is the document *itself* the thing I want to keep, or is it raw material for the wiki to compile? Former → here. Latter → `_inbox/`.

## Conventions

- No frontmatter schema required.
- Any structure you like. Images, tables, code blocks, Mermaid, callouts — all welcome.
- Cross-link freely into the wiki: `[[Large Language Model]]` from inside a reference doc works. Wiki pages can link back to `[[References/<doc>]]`. Backlinks work both ways.
- Sub-folders are fine: `References/Architecture/`, `References/Certifications/AWS-SAA/`, `References/Playbooks/` — whatever organisation fits your material.

## How this differs from the wiki

| | Wiki pages (`AI/`, `Cloud/`, etc.) | References (here) |
|---|---|---|
| Purpose | Compounding concept network | Persistent source documents |
| Schema | Required frontmatter, fixed sections | None — your structure |
| Creation path | Inbox → `vault-ingest` compiles → atomic page | Direct authorship, no pipeline |
| Rewriting | Claude rewrites into the wiki voice on ingestion | Never rewritten — your voice preserved verbatim |
| Validation | `verify-wiki.py` enforces schema | Not validated |
| Images | Usually stripped during ingestion | Preserved as-is |
| Lifetime | Grows over time from many sources | Stays as you wrote it |
| Ingestion triggers | Every push to a matching `_inbox/` path | None; no Action fires on this directory |

## Adding a new reference

Create a new `.md` (or a subfolder + `.md`) under `References/`. Commit, push. Done. No GitHub Action fires. No ingestion. The content is live in Obsidian immediately and stays exactly as you wrote it.

## Extracting concepts from a reference into the wiki

If a reference doc contains concepts that deserve wiki pages, two workflows:

1. **Manual seeding.** While working through the reference doc, drop per-concept inbox files into the relevant `Domain/_inbox/`. Each inbox file cites the reference doc as its source (e.g. `sources: [References/AWS-SAA.md]`). `vault-ingest` compiles those atomic captures into wiki pages. The reference doc stays intact.
2. **On-demand extraction prompt** (optional, for a large reference doc). A Claude prompt can scan a reference doc, identify N concepts worth promoting to wiki pages, and generate one inbox file per concept with citations pointing back. The source doc is read-only throughout.

Either way, the reference doc is never modified by extraction. The wiki becomes a compounding concept network that cross-references the reference library, not a replacement for it.
