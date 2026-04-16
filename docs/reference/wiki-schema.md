# Wiki Page Schema

Every wiki page in the vault must conform to a specific structure. This document defines that structure precisely, because both automated tooling (`vault-ingest`, `verify-wiki.py`) and manual workflows depend on it. Deviations — even small ones like wrong capitalisation in a section heading — will cause validation failures.

## Frontmatter

Each wiki page opens with a YAML frontmatter block. All fields listed below are required unless marked as extended (added automatically by automation):

```yaml
---
title: Page Title
aliases: []
tags:
- Domain/category
type: concept            # see valid types by domain below
domain: AI               # AI | Cloud | Data | Engineering | Homelab
status: stub             # stub (source_count ≤ 1) | draft (2) | mature (≥ 3)
source_count: 1
created: 2026-04-11
updated: 2026-04-11
related:
- '[[Other Page]]'       # MUST be bidirectional
builds_on:
- '[[Other Page]]'       # prerequisite concepts (one-directional)
contrasts_with: []       # opposing concepts (one-directional); default empty
appears_in: []
# Extended fields (added by luminary-scan Action):
# origin: luminary-scan
# luminary: Name
---
```

The `tags` field uses the `Domain/category` format to mirror the directory structure. For example, a page at `AI/concepts/Attention Mechanism.md` would have `tags: [AI/concepts]`. This drives the Obsidian `.base` views.

The `appears_in` field is populated automatically by the `vault-ingest` Action when a page is referenced in project or session notes. It records which project contexts a concept has appeared in. Leave it as `[]` when creating pages manually.

## Valid Types by Domain

The `type` field must match the category subdirectory the page lives in. `verify-wiki.py` cross-checks these:

| Domain | Valid types |
|--------|------------|
| AI | `concept` · `model` · `technique` · `tool` |
| Cloud | `service` · `pattern` · `architecture` |
| Data | `concept` · `algorithm` · `workflow` · `tool` |
| Engineering | `practice` · `tool` · `pattern` |
| Homelab | `hardware` · `os` · `service` |

A page physically located at `AI/tools/LangChain.md` must have `type: tool` and `domain: AI`. Mismatches between the filesystem location and the frontmatter fields are a common source of validation errors when pages are moved between categories.

## Status Values

Status reflects how thoroughly a page has been sourced. It derives directly from `source_count`:

- **stub**: `source_count ≤ 1` — new or single-source page; content may be thin
- **draft**: `source_count = 2` — two distinct sources; more complete but not yet mature
- **mature**: `source_count ≥ 3` — three or more sources; considered authoritative

`verify-wiki.py` validates that `status` is consistent with `source_count`. If you manually add sources to a page and increment `source_count`, update `status` to match. The `.base` Obsidian views (`wiki-stubs.base`, `wiki-mature.base`) filter by these values, so stale status fields produce misleading views.

## Required Body Sections

Every wiki page body must contain these four sections, with exact heading text:

```
## How It Works
## Tensions & Open Questions
## See Also
## Sources
```

Both `vault-ingest` and `verify-wiki.py` check for these exact strings. Capitalisation and punctuation must match precisely:

- `How It Works` — not `How it works`, not `How It Works:`
- `Tensions & Open Questions` — the ampersand is literal, not `and`
- `See Also` — not `See also`, not `See Also:`
- `Sources` — not `References`, not `Links`

The purpose of requiring these sections is to enforce consistent page structure across a large wiki where many authors and automated processes contribute content. `How It Works` provides the conceptual explanation; `Tensions & Open Questions` captures known limitations and unresolved debates; `See Also` holds narrative cross-references; `Sources` lists the citations that back `source_count`.

## The Bidirectional Reciprocal Rule

The `related:` field enforces bidirectional links. If Page A lists `[[Page B]]` in its `related:` field, then Page B must list `[[Page A]]` in its own `related:` field. `verify-wiki.py` checks this for every page in the vault and reports violations.

The reasoning: Obsidian's graph view and backlink panel depend on explicit wikilinks to surface connections. A one-sided `related:` entry means the relationship only appears in one direction in the graph, which is misleading for a field explicitly named "related" (implying mutual relevance).

This rule applies **only to `related:`**. The other two relationship types are intentionally one-directional:

- `builds_on:` — prerequisite concepts. Page A builds on Page B; it does not follow that Page B builds on Page A. No reciprocation required.
- `contrasts_with:` — opposing concepts. Conceptually symmetric, but the field is treated as one-directional to avoid requiring coordinated edits across both pages every time a contrast relationship is added.

When `verify-wiki.py` reports a reciprocation error, the fix is to open the target page and add the source page to its `related:` field — not to remove the link from the source page.

## YAML Editing Warning

**Never use `yaml.safe_load` → re-serialize to edit frontmatter. It corrupts `builds_on` and `appears_in` list fields.**

The specific failure: PyYAML re-serializes multi-value list fields in block style, which conflicts with how Obsidian parses frontmatter. The result is frontmatter that appears syntactically valid but is silently misread by Obsidian — field values may be dropped, merged incorrectly, or displayed as raw strings rather than parsed lists. The corruption is not immediately visible in the file content, which makes it especially dangerous in batch operations.

The correct approach is raw text manipulation or targeted line edits. When `vault-ingest` or any other script needs to update a single frontmatter field (for example, incrementing `source_count` or updating `updated`), it should locate the relevant line with a regex match and replace only that line, leaving all surrounding YAML untouched.

If you are writing a script that modifies wiki frontmatter, use line-by-line text processing rather than loading the full YAML document.

## Template

A canonical empty wiki page template is at `Templates/wiki-page.md` in the vault root. Use this as the starting point when creating pages manually. It includes all required frontmatter fields with placeholder values and all four required body section headings.
