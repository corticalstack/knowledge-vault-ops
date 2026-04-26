# {Repo Name}

> This CLAUDE.md gives Claude vault-awareness scoped to this specific project.
> The global ~/.claude/CLAUDE.md handles session-start pulls and the general
> capture workflow. This file adds the project-specific context Claude needs
> to aim captures accurately and write well-formed inbox files without prompting.
>
> Personalise every section marked with {braces}, then delete this header block.

## Project context

This is a {one-line description of what this repo does}.
Primary language / stack: {e.g. Python, FastAPI, PostgreSQL}.
Primary vault domain for captures from this repo: **{AI|Cloud|Data|Engineering|Homelab}**.

When capturing from sessions in this repo:
- General concepts → `/path/to/your-vault/{Domain}/_inbox/`
- Architectural decisions specific to this repo → `/path/to/your-vault/projects/{repo-name}/_inbox/`
- Cross-repo patterns or gotchas → `/path/to/your-vault/agents-shared/_inbox/`

## Project-specific capture heuristics

In addition to the global auto-flag conditions, proactively suggest capturing when:
- {e.g. "A new API contract is designed — capture the design rationale"}
- {e.g. "A performance optimisation is applied — capture the tradeoff"}
- {e.g. "A third-party library is chosen over an alternative — capture the why"}

## Inbox file format

> The vault's CLAUDE.md holds the authoritative schema, but that file is only
> loaded inside the vault repo. Include the schema here so Claude can write
> well-formed inbox files from any session in this repo.

```yaml
---
sources:
- https://example.com/article   # or "direct observation" for session captures
luminary: null                   # null for manual captures; luminary name for scan-sourced
date: YYYY-MM-DD
domain: {AI|Cloud|Data|Engineering|Homelab}
capture_type: new_concept        # new_concept | enrichment
enriches:                        # omit for new_concept; [[Page Name]] for enrichment
origin: manual                   # manual | luminary-scan
---

## Summary

One paragraph. What is this concept / decision / pattern?

## Key Points

- Bullet per distinct claim. Each should be independently useful.

## Connections

- [[Existing Wiki Page]] — how this relates
- [[Another Page]] — contrast or dependency

## Source Quote / Key Excerpt

> Paste the most important verbatim extract here, or "N/A" for session captures.
```
