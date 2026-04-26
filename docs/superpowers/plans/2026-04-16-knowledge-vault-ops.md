# knowledge-vault-ops Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build out the knowledge-vault-ops repo as a complete reference and replication guide for the knowledge-vault system — covering every component from Day 0 graphify bootstrap through nightly luminary scanning.

**Architecture:** Static documentation repo with no build step. A standalone README serves as the narrative entry point. `docs/` provides deep reference organised by audience (concepts for understanding, reference for operation, setup for replication). `templates/` holds copyable files mirrored from the live source vault at `/mnt/c/Users/jonpaulboyd/Documents/knowledge-vault`.

**Tech Stack:** Markdown, YAML, Python (add_frontmatter.py template), GitHub Actions YAML

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `CLAUDE.md` | Create | Source vault pointer + writing register for this repo |
| `README.md` | Create | Standalone explainer: problem → solution → architecture → setup pointer |
| `docs/concepts/llm-wiki-pattern.md` | Create | Core insight: pre-compile vs. search-time retrieval |
| `docs/concepts/design-principles.md` | Create | 5 principles behind every structural decision |
| `docs/reference/vault-structure.md` | Create | Folder layout, domain map, wiki vs. infrastructure files |
| `docs/reference/wiki-schema.md` | Create | Full frontmatter spec, valid types, required sections, YAML warning |
| `docs/reference/verify-wiki.md` | Create | Script checks, when to run, output format |
| `docs/reference/inbox-workflow.md` | Create | 3 inbox types, trigger mechanism, manual usage |
| `docs/reference/github-actions.md` | Create | Full vault-ingest.yml, Claude prompt intent, guard conditions |
| `docs/reference/luminary-scan.md` | Create | Full luminary-scan.yml, novelty filter, per-luminary commit cadence |
| `docs/reference/graphify.md` | Create | Day-0 usage, ongoing incremental use, reading GRAPH_REPORT.md |
| `docs/reference/agent-memory.md` | Create | projects/ + agents-shared/ structure, session capture workflow |
| `docs/reference/claude-md-conventions.md` | Create | Two-layer CLAUDE.md architecture (global + vault-specific) |
| `docs/setup/prerequisites.md` | Create | GitHub repo, Obsidian Git, Claude Code CLI sub, secrets |
| `docs/setup/quick-start.md` | Create | Day-0 sequence end-to-end |
| `docs/setup/configuration.md` | Create | Domain map, luminaries roster, cron schedule customisation |
| `docs/setup/costs.md` | Create | Subscription vs API key, runner minutes, storage |
| `templates/workflows/vault-ingest.yml` | Create | Copy verbatim from source vault |
| `templates/workflows/luminary-scan.yml` | Create | Copy verbatim from source vault |
| `templates/CLAUDE.md` | Create | Copy verbatim from source vault |
| `templates/luminaries.json` | Create | Copy verbatim from source vault (full 43-luminary roster) |
| `templates/wiki-page.md` | Create | Copy verbatim from source vault |
| `templates/inbox-entry.md` | Create | New: blank inbox entry template |
| `templates/add_frontmatter.py` | Create | Copy verbatim from source vault |

---

## Task 1: Scaffold directories and write CLAUDE.md

**Files:**
- Create: `CLAUDE.md`
- Create directories: `docs/concepts/`, `docs/reference/`, `docs/setup/`, `templates/workflows/`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p docs/concepts docs/reference docs/setup templates/workflows
```

- [ ] **Step 2: Write CLAUDE.md**

Create `CLAUDE.md` with this exact content:

```markdown
# knowledge-vault-ops

This repo documents and replicates the knowledge-vault system.

## Source vault

The live source vault is at `/mnt/c/Users/jonpaulboyd/Documents/knowledge-vault`
(GitHub: corticalstack/knowledge-vault).

`templates/` mirrors live files from the source vault. Before updating any template,
read the corresponding live file first, then overwrite the template to match.

| Template file | Source |
|---------------|--------|
| `templates/workflows/vault-ingest.yml` | `.github/workflows/vault-ingest.yml` |
| `templates/workflows/luminary-scan.yml` | `.github/workflows/luminary-scan.yml` |
| `templates/CLAUDE.md` | `CLAUDE.md` |
| `templates/luminaries.json` | `luminary-scan/luminaries.json` |
| `templates/wiki-page.md` | `Templates/wiki-page.md` |
| `templates/add_frontmatter.py` | `docs/scripts/add_frontmatter.py` |

## Writing register

Every doc in this repo must explain *why* decisions were made, not just *what* the
system does. Reference docs must be usable by someone replicating from scratch, not
only by the owner.

Do not reproduce the vault's wiki schema or ingestion rules inline — those are
documented in `docs/reference/wiki-schema.md` and live in `templates/CLAUDE.md`.
```

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "chore: scaffold repo structure and write CLAUDE.md"
```

---

## Task 2: Write README.md

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write README.md**

The README has three acts followed by an architecture overview and a setup pointer. Write it now.

**Act 1 — The problem** (2–3 paragraphs): Thousands of isolated Obsidian notes, barely cross-referencing, each new thing an isolated file. Every query re-derives relationships from scratch. The vault existed but wasn't useful as a knowledgebase — for browsing or for agents.

**Act 2 — The solution** (2–3 paragraphs): Inspired by Andrej Karpathy's post on building a personal wiki: LLMs can pre-compile relationships, cross-references, and synthesis once — not re-derive them on every question. The result serves two audiences simultaneously: you in Obsidian (browsable, richly cross-referenced wiki) and your LLMs/agents (pre-compiled semantic context ready for agentic components). Running graphify over the vault maps its natural structure; Claude authors the wiki pages using the graph as context; automated ingestion keeps it growing without manual housekeeping.

**Act 3 — What this repo is** (1 paragraph): A reference for how the system was built and why every decision was made, plus all templates needed to replicate it from scratch.

**Architecture overview section**: A prose description (not a diagram) of how the components connect as a pipeline:

> graphify maps the vault → frontmatter injection organises notes into domains → Claude compiles wiki pages using the graph as context → inbox mechanism accepts new sources → vault-ingest Action ingests each source into the wiki → luminary-scan Action runs nightly to surface frontier content → agent memory system stores cross-repo learnings

Each component should be one sentence with a link to its reference doc (e.g. `[graphify](docs/reference/graphify.md)`).

**Closing**: "To replicate this system, start with [Prerequisites](docs/setup/prerequisites.md)."

- [ ] **Step 2: Verify README structure**

Confirm the README contains all of:
- The problem framing (isolation, no cross-referencing)
- The Karpathy inspiration
- The two-audience statement (human + agents)
- The pipeline overview with links to all reference docs
- The setup pointer

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: write README standalone explainer"
```

---

## Task 3: Write docs/concepts/

**Files:**
- Create: `docs/concepts/llm-wiki-pattern.md`
- Create: `docs/concepts/design-principles.md`

- [ ] **Step 1: Write docs/concepts/llm-wiki-pattern.md**

Required sections and content:

```markdown
# The LLM Wiki Pattern

## The Core Insight

Two paragraphs contrasting approaches:
- Traditional: notes accumulate; at query time an LLM searches, retrieves fragments, and
  re-derives relationships from scratch on every query. Cross-references, contradictions,
  and synthesis are never persistent.
- Wiki pattern (Karpathy-inspired): an LLM incrementally compiles sources into structured,
  interlinked pages. Relationships, contrasts, and synthesis are computed once and stored.
  Subsequent queries read pre-compiled context — not raw fragments.

## Why It Matters for Agents

One paragraph: agent context windows are finite. Pre-compiled context (a dense wiki page
with wired related: links) gives an agent more signal per token than a folder of raw notes.
The wiki is optimised for agentic consumption, not just human browsing.

## How graphify Enables It

One paragraph: running graphify over raw notes reveals natural knowledge clusters via Leiden
community detection. These clusters define domain structure. Claude then authors wiki pages
using GRAPH_REPORT.md as a map — it knows which concepts cluster together, which are
prerequisites, which contrast. The graph is the scaffolding; Claude is the author.

## The Compounding Effect

One paragraph: every new source enriches existing pages (bumps source_count, adds links).
The wiki gets denser over time. New agents in new repos inherit accumulated knowledge via
the agent memory system. The benefit compounds across sessions and repos.

## See Also

- [Design Principles](design-principles.md)
- [graphify](../reference/graphify.md)
- [Agent Memory](../reference/agent-memory.md)
```

- [ ] **Step 2: Write docs/concepts/design-principles.md**

Required sections and content:

```markdown
# Design Principles

Five principles implicit in every structural decision. Understanding these resolves
ambiguity when the system needs to be extended or adapted.

## 1. Inbox as Transient Interface

Explain: raw source files are deleted after ingestion. The citation lives in ## Sources
on the wiki page. Keeping raw source copies creates duplicate search results in Obsidian
and conflates source material with compiled knowledge. The inbox is a queue, not an archive.

## 2. Bidirectional Links as Contracts

Explain: if Page A lists [[Page B]] in related:, Page B must list [[Page A]] back.
verify-wiki.py enforces this. Why: following any link always surfaces the full
relationship — no dead ends. An unreciprocated link is a bug, not a style choice.

## 3. Agent Memory Crossing Repo Boundaries

Explain: agents-shared/ surfaces cross-repo learnings at every session start, regardless
of which repo is active. Per-repo projects/ context persists architectural decisions that
would otherwise be lost between sessions. Knowledge compounds across repos, not just within them.

## 4. CLAUDE.md as Behaviour Driver

Explain: the more complete CLAUDE.md is, the less per-session prompting is needed for
consistent output. The vault's CLAUDE.md contains the full wiki schema, ingestion rules,
and integrity constraints — this is what makes every vault-ingest run produce schema-compliant
pages without explicit instruction. The global ~/.claude/CLAUDE.md extends this to every repo.

## 5. Graphify as Map, Not Author

Explain: graphify identifies the domain structure (which concepts cluster together,
which are god nodes, which are thin communities). It does not generate wiki content.
Claude is the author; the graph is the map Claude reads before writing. This distinction
matters when deciding when to re-run graphify (after semantic changes) vs. when to skip
(frontmatter fixes, typo edits — no semantic content changed).

## See Also

- [LLM Wiki Pattern](llm-wiki-pattern.md)
```

- [ ] **Step 3: Commit**

```bash
git add docs/concepts/
git commit -m "docs: write concepts — LLM wiki pattern and design principles"
```

---

## Task 4: Write docs/reference/ — wiki system (vault-structure, wiki-schema, verify-wiki)

**Files:**
- Create: `docs/reference/vault-structure.md`
- Create: `docs/reference/wiki-schema.md`
- Create: `docs/reference/verify-wiki.md`

- [ ] **Step 1: Write docs/reference/vault-structure.md**

Required sections:

```markdown
# Vault Structure

## Top-Level Layout

Show the directory tree. Five knowledge domains at top level: AI/, Cloud/, Data/,
Engineering/, Homelab/. Plus: _INDEX.md (cross-domain), CLAUDE.md (schema + instructions),
VAULT_GUIDE.md (human guide), scripts/, docs/, graphify-out/, luminary-scan/,
projects/, agents-shared/, Templates/.

## Domain Structure

Each domain follows this pattern:
  Domain/
    concepts/ (or services/, practices/, etc.)
    _INDEX.md       — domain entry point
    _inbox/         — ingestion queue
    wiki-recent.base
    wiki-stubs.base
    wiki-mature.base

Table of valid category subdirectories per domain:
- AI: concepts/, models/, techniques/, tools/
- Cloud: services/, patterns/, architecture/
- Data: concepts/, algorithms/, workflows/, tools/
- Engineering: practices/, tools/, patterns/
- Homelab: hardware/, os/, services/

## Wiki Pages vs. Infrastructure Files

Important distinction: verify-wiki.py only validates wiki pages in domain/category/
subdirectories. Infrastructure files are NOT validated:
- _INDEX.md files
- _inbox/ directories
- *.base files (Obsidian views)
- CLAUDE.md, VAULT_GUIDE.md
- graphify-out/
- scripts/, docs/, luminary-scan/
- projects/, agents-shared/

## Current Scale

Note the current scale (83 wiki pages across 5 domains, ~450+ notes total) as a
reference point, with the caveat that this grows continuously.
```

- [ ] **Step 2: Write docs/reference/wiki-schema.md**

Required sections — source: artefact briefing section 5 and vault CLAUDE.md:

```markdown
# Wiki Page Schema

## Frontmatter

Reproduce the full YAML frontmatter spec exactly as it appears in the vault CLAUDE.md
(title, aliases, tags, type, domain, status, source_count, created, updated, related,
builds_on, contrasts_with, appears_in — plus extended fields origin and luminary).

Include the valid types table:
- AI: concept · model · technique · tool
- Cloud: service · pattern · architecture
- Data: concept · algorithm · workflow · tool
- Engineering: practice · tool · pattern
- Homelab: hardware · os · service

Status values: stub (source_count ≤ 1) · draft (2) · mature (≥ 3)

## Required Body Sections

The four required sections with exact heading text:
## How It Works
## Tensions & Open Questions
## See Also
## Sources

Explain: vault-ingest and verify-wiki.py check for these exact strings. Do not vary
the capitalisation or punctuation.

## The Bidirectional Reciprocal Rule

Full explanation: if Page A lists [[Page B]] in related:, Page B must list [[Page A]]
in its own related:. verify-wiki.py enforces this. The rule exists so that following
any link always surfaces the full relationship.

## YAML Editing Warning

Reproduce the warning verbatim: Never use yaml.safe_load → re-serialize to edit
frontmatter. It corrupts builds_on and appears_in list fields. Use raw text
manipulation or targeted line edits only.

Explain why: PyYAML re-serializes list fields in block style which breaks how Obsidian
parses them.

## Template

Pointer to templates/wiki-page.md.
```

- [ ] **Step 3: Write docs/reference/verify-wiki.md**

Required sections — source: artefact briefing section 6:

```markdown
# verify-wiki.py

## What It Checks

Bulleted list of all checks (for every wiki page in every domain/category/ directory):
- All required frontmatter fields present
- type valid for the page's domain
- status is one of stub | draft | mature
- source_count is an integer
- All wikilinks in related:, builds_on:, contrasts_with:, appears_in: resolve to real pages
- Bidirectional reciprocal: every entry in related: links back
- All four required body sections present (exact text)

## When to Run

- After every batch of wiki page writes (manual sessions)
- vault-ingest runs it automatically after every ingestion
- Before committing any batch of wiki changes

## Output Format

Two states:
- Clean: `OK — N pages passed all checks.`
- Errors: specific error messages with file paths and field names

## How vault-ingest Uses It

If errors are found, vault-ingest commits a partial result and opens a GitHub issue
rather than silently failing. The issue title is "Vault ingest errors: {inbox file}".

## Location

`scripts/verify-wiki.py` in the vault root. Not included in templates/ — it is
vault-specific (hardcodes the domain/category structure).
```

- [ ] **Step 4: Commit**

```bash
git add docs/reference/vault-structure.md docs/reference/wiki-schema.md docs/reference/verify-wiki.md
git commit -m "docs: write reference — vault structure, wiki schema, verify-wiki"
```

---

## Task 5: Write docs/reference/ — inbox-workflow and github-actions

**Files:**
- Create: `docs/reference/inbox-workflow.md`
- Create: `docs/reference/github-actions.md`

- [ ] **Step 1: Write docs/reference/inbox-workflow.md**

Required sections — source: artefact briefing section 7:

```markdown
# Inbox Workflow

## Purpose

The inbox is the ingestion interface. Every new source enters the vault by being
written to an inbox folder. From there, automation takes over.

## Three Inbox Types

Table with three rows:
| Inbox path | What goes in | Who reads it |
| <Domain>/_inbox/ | New concepts, articles, papers | vault-ingest → creates/enriches wiki page |
| projects/{repo}/_inbox/ | Repo-specific decisions, tradeoffs | vault-ingest → updates context.md or patterns.md |
| agents-shared/_inbox/ | Cross-repo patterns, gotchas | vault-ingest → updates patterns.md or mistakes.md |

## Why Inbox, Not Direct Edit

Three reasons:
1. Keeps the trigger surface clean: the Action fires on */_inbox/*.md path patterns
2. Separates raw source from compiled wiki — the inbox file is deleted after ingestion
3. Keeping raw source copies creates duplicate search results in Obsidian — inbox files
   are transient by design

## The Trigger Mechanism

Explain the chain: drop file into _inbox/ locally in Obsidian → Obsidian Git plugin
auto-commits and pushes → GitHub detects the push → vault-ingest Action fires on the
matching path pattern. The local→GitHub sync is the trigger mechanism.

## Manual Usage from a Claude Code Session

Two patterns:
1. Direct: "integrate new document AI/_inbox/my-topic.md"
2. Capture: "capture this to the vault" — Claude determines inbox, writes, commits, pushes

## Inbox File Format

Pointer to templates/inbox-entry.md. Explain the fields (sources, luminary if applicable,
domain, capture_type, and body sections: Summary, Key Points, Connections, Source Quote).
```

- [ ] **Step 2: Write docs/reference/github-actions.md**

Required sections — source: artefact briefing section 8 + the live vault-ingest.yml:

```markdown
# vault-ingest GitHub Action

## Overview

One paragraph: what it does, when it fires, what it produces.

## Trigger Paths

List all 7 path patterns:
- AI/_inbox/**
- Cloud/_inbox/**
- Data/_inbox/**
- Engineering/_inbox/**
- Homelab/_inbox/**
- projects/**/_inbox/**
- agents-shared/_inbox/**

Also fires on workflow_dispatch (manual).

## Full YAML

Embed the complete vault-ingest.yml content in a yaml code block. Copy verbatim
from the source vault at:
/mnt/c/Users/jonpaulboyd/Documents/knowledge-vault/.github/workflows/vault-ingest.yml

## What the Claude Prompt Instructs

Numbered list of the 6 steps Claude follows per inbox file:
1. Read the inbox file
2. Determine destination type from path (domain wiki / projects / agents-shared)
3. For domain wiki: new page or enrich existing? Write full schema or bump source_count
4. Wire bidirectional links, update category _INDEX.md, cross-reference related pages
5. Run verify-wiki.py — if errors, commit partial + open GitHub issue; else continue
6. Delete the inbox file; commit with "ingest: {title}"

## Guard Condition

Explain: skips if commit message starts with "ingest:" — prevents the action re-triggering
on its own commits. The actor-based guard (github-actions[bot]) is NOT used because
luminary-scan also pushes as github-actions[bot] and its commits must pass through.

## Required Permissions

- contents: write (push commits)
- issues: write (open issues on verify errors)
- id-token: write (OIDC — inherited from workflow defaults)

## Required Secret

CLAUDE_CODE_OAUTH_TOKEN — Claude Code OAuth token (not a raw API key).
```

- [ ] **Step 3: Commit**

```bash
git add docs/reference/inbox-workflow.md docs/reference/github-actions.md
git commit -m "docs: write reference — inbox workflow and vault-ingest action"
```

---

## Task 6: Write docs/reference/luminary-scan.md

**Files:**
- Create: `docs/reference/luminary-scan.md`

- [ ] **Step 1: Write docs/reference/luminary-scan.md**

Required sections — source: artefact briefing section 9 + live luminary-scan.yml:

```markdown
# luminary-scan GitHub Action

## Overview

One paragraph: nightly scan of 43 luminaries across X/Twitter, blogs, HN, arXiv, Papers
With Code, and HuggingFace. Content authored by the luminary, published yesterday, that
passes a novelty filter → written to the appropriate domain inbox → picked up by
vault-ingest.

## Schedule

Cron: `0 23 * * *` (23:00 UTC = midnight CET). Also fires on workflow_dispatch.

## Full YAML

Embed the complete luminary-scan.yml content in a yaml code block. Copy verbatim from:
/mnt/c/Users/jonpaulboyd/Documents/knowledge-vault/.github/workflows/luminary-scan.yml

## What the Claude Prompt Instructs

Per-luminary steps:
1. Read luminaries.json and seen-urls.json
2. Search for content authored by the luminary published yesterday (list all 6 sources)
3. Filter: skip seen URLs, unconfirmed dates, reposts/marketing
4. Judge novelty: grep vault for concept keywords → 3+ strong matches = skip; 1-2 = enrichment; 0 = new concept
5. If signal: write inbox file to {Domain}/_inbox/YYYY-MM-DD-{luminary-slug}-{concept-slug}.md
6. After each luminary: update seen-urls.json, stage only that luminary's files, commit scan({slug}): {summary}, push immediately

## Novelty Filter Design

Explain the 4 filters and their rationale:
- Authorship filter: content must be BY the luminary, not about them
- Date filter: published yesterday only — no old content recirculating
- HN score threshold: ≥ 200 — filters noise from low-engagement posts
- Grep-before-capture: checks existing vault coverage before writing inbox file — avoids re-ingesting well-covered topics

## Per-Luminary Push Cadence

Explain why each luminary commits and pushes individually: vault-ingest is triggered per
push. If all 43 luminaries committed at once, vault-ingest would fire once and might time
out. Per-luminary push means vault-ingest processes each luminary's content independently.

## luminaries.json Schema

```json
{
  "name": "Full Name",
  "slug": "url-safe-slug",
  "twitter_handle": "handle_without_at",
  "blog_url": "https://... or null",
  "focus": "brief description of their domain focus"
}
```

The focus field is used by Claude to calibrate which vault domain the content maps to.

## Guard Condition

`if: github.actor != 'github-actions[bot]'` — prevents the scan re-triggering on its
own pushes. This is the actor-based guard (unlike vault-ingest which uses commit message
prefix). Difference: luminary-scan pushes under github-actions[bot] identity; vault-ingest
must allow those pushes through, so cannot use the actor guard.

## Required Secrets

- CLAUDE_CODE_OAUTH_TOKEN — Claude Code OAuth token
- VAULT_PAT — GitHub Personal Access Token with contents: write scope. Must be a PAT
  (not GITHUB_TOKEN) because each per-luminary push must trigger vault-ingest downstream.
  GITHUB_TOKEN does not trigger further workflow runs; a PAT does.

## Current Roster

43 luminaries spanning ML research, AI engineering, and AI-adjacent domains. Full list
in templates/luminaries.json. Note that blog_url is null for luminaries without a
personal blog — the scan still covers X/Twitter, HN, arXiv, Papers With Code, and HF.
```

- [ ] **Step 2: Commit**

```bash
git add docs/reference/luminary-scan.md
git commit -m "docs: write reference — luminary-scan action"
```

---

## Task 7: Write docs/reference/ — graphify, agent-memory, claude-md-conventions

**Files:**
- Create: `docs/reference/graphify.md`
- Create: `docs/reference/agent-memory.md`
- Create: `docs/reference/claude-md-conventions.md`

- [ ] **Step 1: Write docs/reference/graphify.md**

Required sections — source: artefact briefing section 2:

```markdown
# graphify

## What It Is

Package: `graphifyy` (double y) — `pip install graphifyy`. Runs parallel Claude agents
for semantic extraction over a directory of markdown files, applies Leiden community
detection, produces three outputs.

## Outputs

Table:
| Output | Purpose |
| graph.json | Machine-readable graph (nodes, edges, communities) |
| graph.html | Interactive visual (zoom, pan, click) |
| GRAPH_REPORT.md | Plain-English report: god nodes, surprising connections, hyperedges — the only output an LLM can read directly |

## Day-0 Bootstrap

Step-by-step: run graphify over raw vault → read GRAPH_REPORT.md → identify natural
clusters → define domain folders manually → relocate misplaced notes → run
add_frontmatter.py. Graphify identified the domains; the folder structure was created
manually. Graphify did not automatically create folders.

Include the bootstrap stats from the actual run: 1736-node graph, 1792 edges, 197 Leiden
communities, 21 parallel extraction agents, 446 files, 5 domains identified.

## Ongoing Incremental Use

Commands:
```bash
# Incremental update, entire vault
graphify . --update

# One domain only
graphify AI/ --update
```

Run after every batch of 5+ new wiki pages. Do not run for frontmatter fixes or typo
edits — no semantic content changed.

## Reading GRAPH_REPORT.md

Three uses before a wiki expansion session:
1. Identify thin communities (need more pages)
2. Find god nodes (most-connected concepts — new pages should reference these)
3. Spot surprising cross-domain connections worth wiring as related: links

## Integration with CLAUDE.md

The vault CLAUDE.md instructs Claude to read GRAPH_REPORT.md before answering
architecture or codebase questions. This means Claude always has the graph's community
structure as context when authoring new wiki pages.
```

- [ ] **Step 2: Write docs/reference/agent-memory.md**

Required sections — source: artefact briefing section 10:

```markdown
# Agent Memory System

## Purpose

The vault stores agent knowledge that would otherwise be lost between sessions:
architectural decisions, cross-repo patterns, bugs and gotchas, lessons learned.
This crosses repo boundaries — learnings from one repo are available in all others.

## Directory Structure

projects/{repo-name}/
  context.md         — architectural decisions and tradeoffs for this repo
  patterns.md        — conventions and preferred patterns
  _inbox/            — session captures queue

agents-shared/
  INDEX.md           — read at every session start (all repos)
  patterns.md        — cross-repo conventions
  mistakes.md        — bugs and gotchas to avoid
  _inbox/

lessons-learned/{domain}/
  {lesson-title}.md  — one file per lesson, domain-organised

## How It Works in Practice

Session capture: say "capture this to the vault" → Claude determines the right inbox
(per-repo or agents-shared) → writes a summary → commits and pushes → vault-ingest
fires and updates the right context.md/patterns.md.

Session start: Claude reads agents-shared/INDEX.md — this surfaces cross-repo lessons
without reading every file. If projects/{this-repo}/context.md exists, it is also read.

## What Gets Captured

Four trigger heuristics:
1. Novel technology stack not yet in the wiki discussed in depth
2. Non-obvious tradeoff that took significant reasoning to resolve
3. Bug's root cause that wasn't documented in any source
4. Architectural decision with a "why" not visible in the code

## agents-shared/INDEX.md

This file is the cross-repo entry point — it must be kept current as patterns.md and
mistakes.md grow. It contains a table of files and a Key Entries section summarising
the most important patterns and mistakes so Claude can act on them from INDEX.md alone
without reading the full files.
```

- [ ] **Step 3: Write docs/reference/claude-md-conventions.md**

Required sections — source: artefact briefing section 11 + user's global ~/.claude/CLAUDE.md:

```markdown
# CLAUDE.md Conventions

## Two-Layer Architecture

The vault system uses two CLAUDE.md files with distinct responsibilities:

| File | Scope | Contains |
|------|-------|---------|
| `~/.claude/CLAUDE.md` | Global — every repo | Session-start instructions, vault capture workflow, auto-flag heuristics |
| `knowledge-vault/CLAUDE.md` | Vault repo only | Wiki schema, ingestion rules, bidirectional link rule, YAML warning |

The global file makes Claude aware of the vault in every session. The vault-specific file
makes Claude a consistent wiki maintainer when working inside the vault.

## Layer 1: Global ~/.claude/CLAUDE.md

What it contains:
- **Session start instructions** (run automatically, without being asked): git pull the
  vault, read agents-shared/INDEX.md, read projects/{this-repo}/context.md if it exists
- **Capture workflow**: how to write to the right inbox, commit message format, the
  git push sequence
- **Auto-flag heuristics**: four conditions that trigger a proactive capture suggestion
- **Bootstrap instructions**: how to set up a new repo in the vault (context.md + patterns.md)

What a replicator must add to their own global CLAUDE.md:
1. The vault path (replace `/mnt/c/Users/jonpaulboyd/Documents/knowledge-vault` with
   their own path)
2. The GitHub remote (replace `corticalstack/knowledge-vault` with their own)
3. The session-start block (git pull, INDEX.md read, per-repo context read)
4. The capture and auto-flag sections

A starting-point template is not provided for the global CLAUDE.md — its content is
tightly coupled to the vault path and GitHub remote, so it must be personalised. Use the
content in this section as the reference for what it must contain.

## Layer 2: knowledge-vault/CLAUDE.md

What it contains:
- graphify integration rules
- Full wiki page schema (frontmatter fields, valid types, required body sections)
- Inbox ingestion workflow (step-by-step)
- YAML editing warning
- Agent memory system structure and session capture workflow

This file is the behaviour driver for consistent wiki maintenance. The more complete it
is, the less per-session prompting is needed. It is mirrored in templates/CLAUDE.md.

## The Principle

Instructions live in CLAUDE.md, not in per-session prompts. A Claude session with a
complete CLAUDE.md produces schema-compliant wiki pages without being told the schema.
A session without it requires explicit instruction every time.
```

- [ ] **Step 4: Commit**

```bash
git add docs/reference/graphify.md docs/reference/agent-memory.md docs/reference/claude-md-conventions.md
git commit -m "docs: write reference — graphify, agent memory, CLAUDE.md conventions"
```

---

## Task 8: Write docs/setup/

**Files:**
- Create: `docs/setup/prerequisites.md`
- Create: `docs/setup/quick-start.md`
- Create: `docs/setup/configuration.md`
- Create: `docs/setup/costs.md`

- [ ] **Step 1: Write docs/setup/prerequisites.md**

Required sections — source: artefact briefing section 1:

```markdown
# Prerequisites

## GitHub Repository

Requirements: standard git repo pushed to GitHub. The two Actions need contents: write
permission to push commits back. Note: self-hosted or other CI platforms would need
adaptation — the Actions assume GitHub-hosted runners.

## Obsidian Git Plugin

Install: Obsidian → Community plugins → "Obsidian Git". Configuration used:
- Auto-pull on startup: enabled
- Auto-push after file change: enabled (or on commit interval)
- Commit message: `vault backup: {{date}}`

Why it matters: Obsidian Git is the trigger mechanism. Dropping a file into _inbox/
in Obsidian → plugin commits and pushes → GitHub sees the push → vault-ingest fires.

## Claude Code CLI Subscription

Install: `npm install -g @anthropic-ai/claude-code`

Both Actions use `claude -p` (headless mode) authenticated via CLAUDE_CODE_OAUTH_TOKEN.
This is a Claude Code subscription token, not a raw Anthropic API key. The distinction
matters: subscription covers Action runs with no per-token cost.

## Required GitHub Secrets

Table:
| Secret | Used by | What it is |
| CLAUDE_CODE_OAUTH_TOKEN | Both Actions | Claude Code OAuth token from your Claude account |
| VAULT_PAT | luminary-scan only | GitHub PAT with contents: write scope |

Why VAULT_PAT and not GITHUB_TOKEN for luminary-scan: GITHUB_TOKEN does not trigger
further workflow runs. luminary-scan must trigger vault-ingest downstream with each
per-luminary push. A PAT does trigger further workflows; GITHUB_TOKEN does not.

How to get CLAUDE_CODE_OAUTH_TOKEN: documented in the Claude Code CLI authentication
settings. It is the OAuth token from your Claude account, not an API key from
console.anthropic.com.
```

- [ ] **Step 2: Write docs/setup/quick-start.md**

Required sections — source: artefact briefing Day 0 sequence:

```markdown
# Quick Start

## Day-0 Sequence

Step-by-step numbered list:

1. **Install graphify**: `pip install graphifyy`
2. **Run graphify over your vault**: `graphify /path/to/vault` — produces graphify-out/
3. **Read GRAPH_REPORT.md**: identify natural clusters. These become your domain folders.
4. **Create domain folder structure manually**: AI/, Cloud/, Data/, etc. with category
   subdirectories (concepts/, models/, etc.) and _inbox/ in each domain.
5. **Create _INDEX.md files**: one per domain (entry point) and one at vault root
   (cross-domain map).
6. **Relocate misplaced notes**: move any notes in the wrong domain folder. 
7. **Run add_frontmatter.py**: `python templates/add_frontmatter.py --apply` (dry run
   first without --apply). Injects stub YAML frontmatter across all notes that lack it.
8. **Begin wiki compilation**: give Claude GRAPH_REPORT.md as context and ask it to
   build wiki pages for each domain. Use templates/wiki-page.md as the template.
9. **Run verify-wiki.py**: fix any reported errors before committing.
10. **Copy workflow YAMLs**: copy templates/workflows/ to .github/workflows/ in your vault repo.
11. **Copy templates/CLAUDE.md** to your vault root.
12. **Add GitHub secrets**: CLAUDE_CODE_OAUTH_TOKEN and VAULT_PAT.
13. **Test vault-ingest**: drop a file into any _inbox/, push, watch the Action run.
14. **Test luminary-scan**: trigger manually via workflow_dispatch.

## Verify It's Working

- vault-ingest: the inbox file should be deleted and a new wiki page (or enriched page)
  should appear in a commit starting with "ingest:".
- luminary-scan: commits starting with "scan({slug}):" should appear, and any captured
  content should trigger vault-ingest.
```

- [ ] **Step 3: Write docs/setup/configuration.md**

Required sections:

```markdown
# Configuration

Decisions a replicator must personalise. Everything else can be copied verbatim from templates/.

## Domain Map

Default: AI, Cloud, Data, Engineering, Homelab.

To use different domains:
1. Change top-level folder names in your vault
2. Update vault-ingest.yml trigger paths (AI/_inbox/**, etc.) to match your domains
3. Update the DOMAIN_MAP in add_frontmatter.py
4. Update vault CLAUDE.md valid domain list
5. Run graphify to discover your vault's natural clusters — let the graph suggest domains

## Luminaries Roster

Start from templates/luminaries.json (43 entries). Edit to match your focus areas:
- Remove luminaries outside your domains
- Add luminaries: use the schema (name, slug, twitter_handle, blog_url, focus)
- The focus field calibrates Claude's domain classification — be specific

Keep the file at luminary-scan/luminaries.json in your vault root.

## Cron Schedule

Default: `0 23 * * *` (23:00 UTC). Change the schedule line in luminary-scan.yml.
Note: each luminary scan can take 1-3 minutes; 43 luminaries = up to 2 hours.
The Action has timeout-minutes: 60 — adjust if your roster is large.

## Vault Path in Global CLAUDE.md

Replace `/mnt/c/Users/jonpaulboyd/Documents/knowledge-vault` with your vault path in
your global ~/.claude/CLAUDE.md.

## seen-urls.json

Initialise as an empty array: `[]`. luminary-scan appends to this file after each run.
Location: luminary-scan/seen-urls.json in your vault root.
```

- [ ] **Step 4: Write docs/setup/costs.md**

Required sections:

```markdown
# Costs

## Claude Code Subscription

Both Actions use claude -p authenticated via a Claude Code OAuth token. If you have a
Claude Code subscription, Action runs are covered — there is no additional per-token API
cost. This is the approach used in this system.

## Raw API Key Alternative

If you do not have a Claude Code subscription, you can replace claude -p with direct
Anthropic API calls. This incurs per-token costs. Rough estimates for a single
vault-ingest run (one inbox file): ~$0.01–0.05 depending on page complexity and model.
Luminary-scan with 43 luminaries: ~$1–3 per nightly run depending on how much content
is found.

## GitHub Actions Runner Minutes

Both Actions run on ubuntu-latest (GitHub-hosted). Free tier includes 2,000 minutes/month
for public repos and 2,000 minutes/month for private repos (GitHub Free plan).

- vault-ingest: typically 2–5 minutes per run
- luminary-scan: up to 60 minutes per run (timeout)

For a vault with active daily use (1–2 inbox drops/day + nightly scan): ~90–120 minutes/month.
Well within the free tier.

## Storage

The vault grows continuously as wiki pages are added. No special storage considerations
beyond normal git repo limits. GitHub's 1GB soft limit for repos is unlikely to be
reached by a text-only vault.
```

- [ ] **Step 5: Commit**

```bash
git add docs/setup/
git commit -m "docs: write setup — prerequisites, quick-start, configuration, costs"
```

---

## Task 9: Copy template workflow YAMLs

**Files:**
- Create: `templates/workflows/vault-ingest.yml`
- Create: `templates/workflows/luminary-scan.yml`

Source files are at:
- `/mnt/c/Users/jonpaulboyd/Documents/knowledge-vault/.github/workflows/vault-ingest.yml`
- `/mnt/c/Users/jonpaulboyd/Documents/knowledge-vault/.github/workflows/luminary-scan.yml`

- [ ] **Step 1: Read and copy vault-ingest.yml**

Read `/mnt/c/Users/jonpaulboyd/Documents/knowledge-vault/.github/workflows/vault-ingest.yml`
then write the content verbatim to `templates/workflows/vault-ingest.yml`.

- [ ] **Step 2: Read and copy luminary-scan.yml**

Read `/mnt/c/Users/jonpaulboyd/Documents/knowledge-vault/.github/workflows/luminary-scan.yml`
then write the content verbatim to `templates/workflows/luminary-scan.yml`.

- [ ] **Step 3: Verify both files are complete**

Both files must start with `name:` and contain at least one job with `runs-on: ubuntu-latest`.

```bash
head -3 templates/workflows/vault-ingest.yml
head -3 templates/workflows/luminary-scan.yml
```

Expected:
```
name: Vault Ingest
...
name: Luminary Scan
```

- [ ] **Step 4: Commit**

```bash
git add templates/workflows/
git commit -m "templates: add vault-ingest and luminary-scan workflow YAMLs"
```

---

## Task 10: Copy remaining templates and create inbox-entry.md

**Files:**
- Create: `templates/CLAUDE.md`
- Create: `templates/luminaries.json`
- Create: `templates/wiki-page.md`
- Create: `templates/add_frontmatter.py`
- Create: `templates/inbox-entry.md`

Source files:
- `templates/CLAUDE.md` ← `/mnt/c/Users/jonpaulboyd/Documents/knowledge-vault/CLAUDE.md`
- `templates/luminaries.json` ← `/mnt/c/Users/jonpaulboyd/Documents/knowledge-vault/luminary-scan/luminaries.json`
- `templates/wiki-page.md` ← `/mnt/c/Users/jonpaulboyd/Documents/knowledge-vault/Templates/wiki-page.md`
- `templates/add_frontmatter.py` ← `/mnt/c/Users/jonpaulboyd/Documents/knowledge-vault/docs/scripts/add_frontmatter.py`

- [ ] **Step 1: Read and copy CLAUDE.md**

Read `/mnt/c/Users/jonpaulboyd/Documents/knowledge-vault/CLAUDE.md` and write verbatim
to `templates/CLAUDE.md`.

- [ ] **Step 2: Read and copy luminaries.json**

Read `/mnt/c/Users/jonpaulboyd/Documents/knowledge-vault/luminary-scan/luminaries.json`
and write verbatim to `templates/luminaries.json`.

- [ ] **Step 3: Read and copy wiki-page.md**

Read `/mnt/c/Users/jonpaulboyd/Documents/knowledge-vault/Templates/wiki-page.md` and
write verbatim to `templates/wiki-page.md`.

- [ ] **Step 4: Read and copy add_frontmatter.py**

Read `/mnt/c/Users/jonpaulboyd/Documents/knowledge-vault/docs/scripts/add_frontmatter.py`
and write verbatim to `templates/add_frontmatter.py`.

- [ ] **Step 5: Create templates/inbox-entry.md**

Write the following content:

```markdown
---
sources:
- https://example.com/source-url
luminary: null
date: YYYY-MM-DD
domain: AI
capture_type: new_concept
enriches: null
origin: manual
---
# Concept Title

## Summary

2-3 sentences capturing the core idea in plain language.

## Key Points

- key point
- key point
- key point

## Connections

- [[Existing Vault Page]] — brief reason for the connection

## Source Quote / Key Excerpt

> Direct quote or close paraphrase from the original source.
```

Notes on fields:
- `luminary`: null for manual captures; luminary name for scan-generated files
- `capture_type`: `new_concept` or `enrichment`
- `enriches`: null for new concepts; `[[Page Name]]` for enrichments
- `origin`: `manual` or `luminary-scan`

- [ ] **Step 6: Verify template file count**

```bash
find templates/ -type f | sort
```

Expected output (7 files):
```
templates/CLAUDE.md
templates/add_frontmatter.py
templates/inbox-entry.md
templates/luminaries.json
templates/wiki-page.md
templates/workflows/luminary-scan.yml
templates/workflows/vault-ingest.yml
```

- [ ] **Step 7: Commit**

```bash
git add templates/
git commit -m "templates: add CLAUDE.md, luminaries.json, wiki-page, inbox-entry, add_frontmatter.py"
```
