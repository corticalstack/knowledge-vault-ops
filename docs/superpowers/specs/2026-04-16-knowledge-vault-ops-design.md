# knowledge-vault-ops Design

**Date:** 2026-04-16
**Status:** Approved

## Purpose

Document the design and rationale for the `knowledge-vault-ops` repository — a reference and replication guide for the knowledge-vault system: an Obsidian vault restructured into a living, agent-ready knowledgebase backed by automated ingestion and nightly frontier scanning.

The repo serves two audiences simultaneously:
- **Owner** — reference for how and why the system was built
- **Replicator** — enough detail to reproduce the system from scratch

---

## Repo Structure

```
knowledge-vault-ops/
├── README.md
├── CLAUDE.md
├── docs/
│   ├── concepts/
│   │   ├── llm-wiki-pattern.md
│   │   └── design-principles.md
│   ├── reference/
│   │   ├── vault-structure.md
│   │   ├── wiki-schema.md
│   │   ├── inbox-workflow.md
│   │   ├── github-actions.md
│   │   ├── luminary-scan.md
│   │   ├── graphify.md
│   │   ├── agent-memory.md
│   │   ├── verify-wiki.md
│   │   └── claude-md-conventions.md
│   └── setup/
│       ├── prerequisites.md
│       ├── quick-start.md
│       ├── configuration.md
│       └── costs.md
└── templates/
    ├── workflows/
    │   ├── vault-ingest.yml
    │   └── luminary-scan.yml
    ├── CLAUDE.md
    ├── luminaries.json
    ├── wiki-page.md
    ├── inbox-entry.md
    └── add_frontmatter.py
```

---

## Content Strategy

### README.md

Three acts:

1. **The problem** — thousands of isolated Obsidian notes, no cross-referencing, every new thing an isolated file
2. **The solution** — Karpathy-inspired pattern: LLMs pre-compile relationships once rather than re-derive on every query; graphify runs semantic extraction and community detection to map the vault; the result serves both human browsing and agentic context
3. **Architecture overview** — how graphify → frontmatter injection → wiki compilation → inbox mechanism → vault-ingest → luminary-scan all connect as a pipeline

Ends with a pointer to `docs/setup/prerequisites.md` for replication. The LinkedIn origin story is woven into act 1/2 — no separate narrative file.

### docs/concepts/

**`llm-wiki-pattern.md`** — The core insight: a wiki pre-compiles relationships (cross-references, contradictions, synthesis) so agents don't re-derive them at query time. Contrasts with raw note search. Traces the Karpathy influence.

**`design-principles.md`** — Five principles implicit in every structural decision:
1. Inbox as transient interface (raw source deleted after ingestion; citation lives on the wiki page)
2. Bidirectional links as contracts (enforced by verify-wiki.py — no dead ends)
3. Agent memory crossing repo boundaries (agents-shared/ + per-repo projects/)
4. CLAUDE.md as behaviour driver (the more complete it is, the less per-session prompting is needed)
5. Graphify as map, not author (graph identifies domains; Claude authors the pages)

### docs/reference/

Each file is sourced from the corresponding section of the artefact briefing. Full YAML is embedded inline in `github-actions.md` and `luminary-scan.md` — not linked out.

**`vault-structure.md`** — Domain folder layout, category subdirectories, the distinction between wiki pages and infrastructure files (\_INDEX.md, \*.base, CLAUDE.md, graphify-out/, scripts/).

**`wiki-schema.md`** — Complete frontmatter spec (all fields, valid types per domain, status values), required body sections (exact heading text), the bidirectional reciprocal rule, YAML editing warning (never safe\_load → re-serialize).

**`inbox-workflow.md`** — Three inbox types (domain, per-repo, agents-shared), trigger mechanism (Obsidian Git plugin → push → Action fires), manual usage from a Claude Code session.

**`github-actions.md`** — Full vault-ingest.yml YAML, guard conditions (skip if commit starts with `ingest:`), what the Claude prompt instructs step by step, error path (partial commit + GitHub issue).

**`luminary-scan.md`** — Full luminary-scan.yml YAML, novelty filter design (authorship filter, date filter, HN score threshold, grep-before-capture), per-luminary commit-and-push cadence, luminaries.json schema.

**`graphify.md`** — Day-0 bootstrap usage (pip install graphifyy, outputs, how GRAPH\_REPORT.md drove domain discovery), ongoing incremental use (`--update` flag), when to run vs. when to skip, reading the report before a wiki expansion session.

**`agent-memory.md`** — projects/{repo}/ structure (context.md, patterns.md, \_inbox/), agents-shared/ structure (INDEX.md, patterns.md, mistakes.md), how session captures flow from conversation to vault to future sessions.

**`verify-wiki.md`** — What the script checks (frontmatter completeness, valid type/status, wikilink resolution, bidirectional reciprocal, required sections), when to run it, output format, how vault-ingest uses it.

**`claude-md-conventions.md`** — Two-layer architecture:
- Layer 1: `~/.claude/CLAUDE.md` (global) — session-start instructions for every repo (vault pull, INDEX.md read, per-repo context read), capture workflow, auto-flag heuristics, bootstrap instructions. What a replicator must add to their own global CLAUDE.md.
- Layer 2: `knowledge-vault/CLAUDE.md` (vault-specific) — wiki schema, ingestion rules, bidirectional link rule, YAML editing warning. Sourced directly from `templates/CLAUDE.md`.

### docs/setup/

**`prerequisites.md`** — GitHub repo requirements (contents: write permission), Obsidian Git plugin configuration, Claude Code CLI subscription (not API key — distinction matters for cost), required GitHub secrets (CLAUDE\_CODE\_OAUTH\_TOKEN, VAULT\_PAT and why PAT not GITHUB\_TOKEN).

**`quick-start.md`** — Day-0 sequence end-to-end: run graphify → read GRAPH\_REPORT.md → define domains → create folder structure → relocate notes → run add\_frontmatter.py → begin wiki compilation with Claude → wire GitHub Actions → test with a manual inbox drop.

**`configuration.md`** — Decisions a replicator must personalise: domain map (their vault's natural clusters from graphify), luminaries roster (start from templates/luminaries.json, add/remove for their focus areas), cron schedule (default 23:00 UTC), inbox path patterns if domains differ.

**`costs.md`** — Claude Code subscription covers Action runs (no per-token cost), GitHub-hosted runner minutes (free tier sufficient for both Actions), storage (vault size dependent). Comparison: what this would cost on a raw API key.

### templates/

Files copied or adapted from the live source vault:

| File | Source |
|------|--------|
| `workflows/vault-ingest.yml` | `.github/workflows/vault-ingest.yml` in knowledge-vault |
| `workflows/luminary-scan.yml` | `.github/workflows/luminary-scan.yml` in knowledge-vault |
| `CLAUDE.md` | `CLAUDE.md` in knowledge-vault root |
| `luminaries.json` | `luminary-scan/luminaries.json` — full 43-luminary roster |
| `wiki-page.md` | `Templates/wiki-page.md` in knowledge-vault |
| `inbox-entry.md` | Blank template with stub frontmatter (new file) |
| `add_frontmatter.py` | `docs/scripts/add_frontmatter.py` in knowledge-vault |

When the source vault updates a template file, update the corresponding file in `templates/` to match.

### CLAUDE.md (this repo)

Two responsibilities:

1. **Source vault pointer** — `templates/` mirrors live files from `/mnt/c/Users/jonpaulboyd/Documents/knowledge-vault`. Before updating a template, read the live source file first.
2. **Writing register** — every doc in this repo should explain *why* decisions were made, not just *what* the system does. Reference docs must be usable by someone replicating from scratch.

Does not reproduce the vault's wiki schema or ingestion rules — those live in the vault's own CLAUDE.md and are documented in `docs/reference/wiki-schema.md`.

---

## What Is Not In Scope

- The graphify tool itself (external dependency, documented in `docs/reference/graphify.md` by reference)
- The Obsidian vault content (wiki pages, notes) — only the system that maintains them
- verify-wiki.py as a copyable template — it is vault-specific; documented in reference only
- Any UI or visualisation beyond the existing graph.html output from graphify
