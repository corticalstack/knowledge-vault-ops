# knowledge-vault-ops

A reference for how my knowledge-vault system was built, and all the templates needed to replicate it from scratch.

---

## The problem

The vault began as roughly four thousand Obsidian notes accumulated over years of learning. Each note captured something useful in isolation — a concept, a paper summary, a configuration snippet, but the collection as a whole was inert. Concepts that built on each other sat in separate files with no relationship, as linking is really a chore. My vault was a list of documents, not a deep knowledgebase. 

There was also a second failure as I started to think of the potential for using my vault with agentic tooling. It was currently poor for use with agents. A language model given access to four thousand loose markdown files must re-reason about every relationship on every request. There is no pre-computed, shared structure it can lean on, no pre-built map of what connects to what or why, no concept overview.

---

## The solution

Inspiration came from Andrej Karpathy's [LLM-Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). The key idea is that language models should do the heavy lifting, compilation and note integration work once, not when they are consumed as reference knowledge on every query. Rather than asking an LLM to derive relationships at query time, the LLM runs over notes in advance to extract structure, build cross-references, and synthesise concepts and connections, then store that compiled knowledge that both humans and agents can read directly.

Now, in Obsidian, I get a rich wiki where every page has structured YAML frontmatter encoding `related:`, `builds_on:`, and `contrasts_with:` wikilinks. I can now follow genuine conceptual connections. My agentic tooling gets those same pre-compiled relationships. They can read a wiki page's frontmatter and know what this concept relates to without having to reason about it across multiple raw notes.

To achieve this, an overhaul day-zero bootstrap ran graphify over the vault. Graphify uses Claude as a parallel-agent tool that performs semantic extraction over markdown files, applies Leiden community detection, and produces a plain-English map of the vault's knowledge clusters. For my own notes collection, five natural domains surfaced: AI, Cloud, Data, Engineering, and Homelab. I then got Claude to use the graphify graph as context to author the first generation of wiki pages. New notes I land in an `_inbox/` folder; a GitHub Action fires, Claude reads the note, and decides whether to create a new page or enrich an existing one, and the wiki grows without manual housekeeping. A nightly scan monitors 43 luminaries (frontier researchers) — Karpathy, LeCun, and others — for content they authored in the last day, filters for novelty, and writes inbox files for anything that passes, so frontier ideas reach the wiki automatically.

The compiled wiki is organised around those five domains. Each domain has an index page mapping its conceptual landscape, and below that, individual pages for each concept. The same concept accumulates depth from multiple sources over time rather than generating a new file for each one.

---

## How it works

The system is a pipeline from raw notes to a compounding knowledge base. On Day 0 it discovers the structure of a flat, brownfield vault. Every day after, it ingests new content into that structure.

**Day 0 bootstrap** — four ordered steps, each depending on the previous:

1. **graphify** over the flat vault produces `GRAPH_REPORT.md`: 50–100 fine-grained topical communities, god nodes, cross-domain bridges. The domain structure is *discovered, not designed*, reading the graph indicates the natural corpus shape.
2. **Reorganisation prompt** ([`templates/day-zero-reorganise-prompt.md`](templates/day-zero-reorganise-prompt.md)) handles both domain naming and file moves in one Claude-driven pass with two review gates. I wanted a simple vault hierarchy, so phase 1 rolls graphify's fine-grained communities up into a small set of top-level domain names (for my vault: AI, Cloud, Data, Engineering, Homelab — a different corpus will surface different labels), writes `domain-proposal.md`, and stops for review. Phase 2 classifies every note, writes `reorganise-plan.md`, and stops again. Phase 3 `git mv`s every file into its domain folder — graphify's community assignment is the primary signal, note content is the tiebreaker, and history is preserved so `git log --follow` still works on every note.
3. **`add_frontmatter.py`** stamps every note. Running after step 2, the script derives `domain:` from the top-level folder path, so notes must already sit under their domain folder, or every stamp would be `domain: Unknown`.
4. **Wiki compilation, then category finalisation.** Claude uses `GRAPH_REPORT.md` as context and writes pages from [`templates/wiki-page.md`](templates/wiki-page.md), domain by domain. Category subfolders (`AI/concepts/`, `AI/techniques/`, etc.) emerge during compilation rather than being decided upfront — the category axis (concept / model / technique / tool) is orthogonal to the domain axis and easier to judge once pages have been normalised into wiki form. Once enough pages exist per domain to see the shape, the category finalisation prompt ([`templates/day-zero-categories-prompt.md`](templates/day-zero-categories-prompt.md)) observes which category folders compilation produced, proposes a final per-domain category list, and on approval rewrites the `Valid types:` line in vault `CLAUDE.md` and the `DOMAINS` dict in `scripts/verify-wiki.py` to match. Both files are load-bearing: `vault-ingest` reads `CLAUDE.md` to place new pages in the right category, `verify-wiki.py` walks every `Domain/category/` path and errors on mismatches. Categories, like domains, are *discovered, not designed* — formalised from what compilation actually produced.

**Ongoing operation:**

- **inbox mechanism** — drop a file in any `_inbox/` folder and the pipeline picks it up.
- **[vault-ingest GitHub Action](templates/workflows/vault-ingest.yml)** fires on each inbox file, runs Claude to create or enrich the relevant wiki page, then deletes the source.
- **[luminary-scan GitHub Action](templates/workflows/luminary-scan.yml)** runs nightly to scan 43 frontier researchers, filters for novelty, and writes inbox files for anything new.
- **agent memory system** stores per-repo context in `projects/` and cross-repo learnings in `agents-shared/`, letting Claude carry knowledge between sessions.

### Design principles

**1. Inbox as transient interface.** Raw source files are deleted after ingestion. What persists is not the source but the citation: a reference in the `## Sources` section of the wiki page the source enriched. Keeping raw source copies alongside compiled wiki pages creates duplicate search results in Obsidian and blurs the distinction between source material and compiled knowledge. The inbox is just a queue.

**2. Bidirectional links as contracts.** If Page A lists `[[Page B]]` in its `related:` frontmatter, Page B must list `[[Page A]]` back. This is enforced by `verify-wiki.py`. Following any link should always surface the full relationship — no dead ends, no asymmetric awareness. An unreciprocated link is a structural bug, not a style choice.

**3. CLAUDE.md as behaviour driver.** The more complete a `CLAUDE.md` file is, the less per-session prompting is needed. The vault's [`CLAUDE.md`](templates/CLAUDE.md) contains the full wiki schema, the ingestion workflow, and the integrity constraints in one place. This is what makes every vault-ingest run produce schema-compliant pages without explicit instruction.

**4. Graphify as map, not author.** graphify identifies domain structure; it does not generate wiki content. Claude is the author; the graph is the map Claude reads before writing. Re-run graphify after changes that alter the semantic structure of the corpus.

**5. Agent memory crossing repo boundaries.** The vault's `agents-shared/` directory surfaces cross-repo learnings at the start of every Claude Code session regardless of which repository is active. Per-repo context lives in `projects/{repo-name}/context.md`. Knowledge does not stop at repo boundaries — an agent working in a new repository starts with the accumulated understanding built across all previous repo sessions.

### Vault structure

```
knowledge-vault/
├── AI/                              — wiki domain
├── Cloud/                           — wiki domain
├── Data/                            — wiki domain
├── Engineering/                     — wiki domain
├── Homelab/                         — wiki domain
├── Personal/                        — owner-specific notes (not part of the wiki)
├── Assets/                          — images and attachments
├── References/                      — persistent, full-fidelity knowledge assets (never ingested)
│   └── _INDEX.md                    — what lives here and what does not
├── Templates/
│   └── wiki-page.md                 — starting template for new wiki pages
├── scripts/
│   └── verify-wiki.py               — frontmatter + link integrity check
├── docs/
│   └── scripts/
│       └── add_frontmatter.py       — Day-0 frontmatter stamping script
├── graphify-out/
│   ├── GRAPH_REPORT.md
│   ├── graph.html
│   └── graph.json
├── luminary-scan/
│   ├── luminaries.json
│   └── seen-urls.json
├── lessons-learned/
│   └── {domain}/                    — one file per lesson
├── projects/
│   └── {repo-name}/
│       ├── context.md
│       ├── patterns.md
│       └── _inbox/
├── agents-shared/
│   ├── INDEX.md
│   ├── patterns.md
│   ├── mistakes.md
│   └── _inbox/
├── _INDEX.md                        — cross-domain map and bridge concepts
├── CLAUDE.md                        — schema + instructions for Claude
└── VAULT_GUIDE.md                   — human-readable design guide
```

Each of the five domains follows the same internal pattern:

```
Domain/
├── {category}/                      — wiki pages live here
├── _inbox/                          — ingestion queue
├── _INDEX.md                        — domain entry point
├── wiki-recent.base                 — Obsidian view: all pages by updated date
├── wiki-stubs.base                  — source_count ≤ 1
├── wiki-mature.base                 — source_count ≥ 3
└── wiki-review.base                 — pages flagged for review
```

**Valid category subdirectories per domain:**

| Domain | Valid categories |
|--------|-----------------|
| AI | `concepts/` · `models/` · `techniques/` · `tools/` |
| Cloud | `services/` · `patterns/` · `architecture/` |
| Data | `concepts/` · `algorithms/` · `workflows/` · `tools/` |
| Engineering | `practices/` · `tools/` · `patterns/` |
| Homelab | `hardware/` · `os/` · `services/` |

These names are not arbitrary — `verify-wiki.py` uses them to validate that each page's `type` field matches its location.

**Wiki pages vs infrastructure files.** Wiki pages are `.md` files that live inside a `domain/category/` subdirectory (e.g. `AI/concepts/Large Language Model.md`). Only these files are validated by `verify-wiki.py`. Everything else — `_INDEX.md` files, `_inbox/`, `.base` files, `CLAUDE.md`, `graphify-out/`, `scripts/`, `luminary-scan/`, `projects/`, `agents-shared/`, `lessons-learned/`, `Templates/`, `References/`, `Personal/`, `Assets/` — is infrastructure and is not validated.

### References/ — persistent knowledge assets alongside the wiki

The wiki is not the only home for knowledge. Some content does not fit the compile-and-rewrite model: long-form architecture notes, exam / certification study material, extensive playbooks, documents with many diagrams and images. Feeding these through `vault-ingest` would shatter the linear narrative, strip attachments, and rewrite hand-crafted prose into the wiki voice — information loss by design, not a bug.

`References/` at the vault root is the answer. It is a sibling to the wiki domains, not part of them:

- **Full fidelity.** Markdown in your structure, your voice, no frontmatter schema, no required sections, images and tables and code blocks preserved verbatim.
- **Never ingested.** `vault-ingest` triggers on `*/_inbox/**` paths only — `References/` is invisible to it.
- **Never validated.** `verify-wiki.py` only walks `Domain/category/*.md`; `References/` is out of scope.
- **Never reorganised.** [`templates/day-zero-reorganise-prompt.md`](templates/day-zero-reorganise-prompt.md) and [`templates/day-zero-categories-prompt.md`](templates/day-zero-categories-prompt.md) list it under LEAVE UNTOUCHED.
- **Cross-linkable.** Wiki pages can `[[References/...]]` and reference docs can `[[Large Language Model]]` wiki pages. Backlinks work both ways.

**Three workflows for relating reference docs to the wiki** (choose per document):

1. **Reference only.** The doc lives in `References/` and is linked from wherever relevant. No wiki extraction. Right for architecture docs specific to one project that do not generalise.
2. **Manual concept seeding.** While working through the doc, drop per-concept inbox files into the relevant `Domain/_inbox/` citing the reference doc as source. The wiki accumulates concept pages naturally; the reference doc stays intact.
3. **On-demand extraction.** A separate Claude prompt scans the reference doc, identifies concepts worth promoting to wiki pages, and generates one inbox file per concept with a citation back. The source doc is read-only throughout.

This keeps the llm-wiki concept intact — the wiki remains a compounding network of atomic concepts — while giving your hand-authored knowledge assets a permanent, untouched home. Zero information loss, explicit rather than implicit archival, and compatible with the existing pipeline without modifying `vault-ingest` or `verify-wiki.py`.

Starter content for `References/_INDEX.md` (what lives here, conventions, and the workflow choices above) is at [`templates/references-index.md`](templates/references-index.md).

### Wiki page schema

Every wiki page opens with a YAML frontmatter block. All fields below are required unless marked extended:

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
contrasts_with: []       # opposing concepts (one-directional)
appears_in: []           # populated automatically by vault-ingest
# Extended (added by luminary-scan):
# origin: luminary-scan
# luminary: Name
---
```

**Status values** derive from `source_count`:
- **stub**: `source_count ≤ 1` — new or single-source page
- **draft**: `source_count = 2` — two distinct sources
- **mature**: `source_count ≥ 3` — three or more sources, considered authoritative

A canonical empty template is at [`templates/wiki-page.md`](templates/wiki-page.md).

### Inbox workflow

The inbox is the ingestion interface. Every new source enters the vault by being written to an inbox folder; automation takes over from there.

| Inbox path | What goes in | Who reads it |
|---|---|---|
| `<Domain>/_inbox/` | New concepts, articles, papers | vault-ingest → creates or enriches wiki page |
| `projects/{repo}/_inbox/` | Repo-specific decisions, tradeoffs | vault-ingest → updates `context.md` or `patterns.md` |
| `agents-shared/_inbox/` | Cross-repo patterns, gotchas | vault-ingest → updates `patterns.md` or `mistakes.md` |

**Why inbox, not direct edit:**
1. Clean trigger surface — the Action fires on `*/_inbox/*.md` path patterns.
2. Raw source stays separated from compiled wiki. The inbox file is deleted after ingestion; the citation lives in `## Sources` on the wiki page.
3. Keeping raw source copies creates duplicate search results in Obsidian. Inbox files are transient by design.

**The trigger chain:** drop a file into `_inbox/` locally in Obsidian → the Obsidian Git plugin auto-commits and pushes to GitHub → GitHub detects the push → `vault-ingest` fires because the pushed path matches one of the `*/_inbox/*.md` patterns. There is no polling; every push is evaluated against the path filter.

**Manual usage from a Claude Code session:**
1. **Direct:** "integrate new document AI/_inbox/my-topic.md" — Claude reads the file and processes it inline.
2. **Capture:** "capture this to the vault" — Claude determines the right inbox (domain, per-repo, or agents-shared), writes a well-formed summary, commits, and pushes. vault-ingest fires on the push.

Claude will also proactively suggest capturing when it encounters a novel concept, a non-obvious tradeoff that took significant reasoning to resolve, or a bug root cause not already documented in the vault.

**Inbox file format** — see [`templates/inbox-entry.md`](templates/inbox-entry.md). Key frontmatter fields: `sources`, `luminary` (null for manual), `date`, `domain`, `capture_type` (`new_concept` or `enrichment`), `enriches` (`[[Page Name]]` for enrichments, omit for new concepts), `origin` (`manual` or `luminary-scan`). Body requires four sections: `## Summary`, `## Key Points`, `## Connections`, `## Source Quote / Key Excerpt`.

### graphify

Package: `graphifyy` (double y) — `pip install graphifyy`. Runs parallel Claude agents for semantic extraction over a directory of markdown files, applies Leiden community detection, and produces three outputs in `graphify-out/`:

| Output | Purpose |
|--------|---------|
| `graph.json` | Machine-readable graph (nodes, edges, communities) |
| `graph.html` | Interactive visual |
| `GRAPH_REPORT.md` | Plain-English report — god nodes, surprising connections, hyperedges. The only output an LLM can read directly. |

Source: [https://github.com/safishamsi/graphify](https://github.com/safishamsi/graphify).

**Day-0 bootstrap stats:** 21 parallel extraction agents processed 446 files, producing 1,736 nodes and 1,792 edges across 197 Leiden communities. Five domains were identified: AI, Cloud, Data, Engineering, Homelab. God nodes (highest edge counts): ML Terminology (27), Azure AZ-305 (17), Azure DevOps Pipelines (14). These are vault-specific — your graph will surface different god nodes depending on your corpus.

**Ongoing incremental use:**

```bash
graphify . --update         # whole vault
graphify AI/ --update       # one domain
```

Run after every batch of 5+ new wiki pages. Skip it for frontmatter fixes or typo edits — no semantic content changed.

**Reading `GRAPH_REPORT.md` before a wiki session:**
1. **Identify thin communities** — clusters with few pages signal gaps worth filling next.
2. **Find god nodes** — structural anchors. New pages on related topics should reference these.
3. **Spot surprising cross-domain connections** — candidates for `related:` links across domain folders.

The vault `CLAUDE.md` instructs Claude to read `GRAPH_REPORT.md` before answering architecture questions, so Claude always has the graph as context when authoring new pages.

### vault-ingest Action

Fires on any push to `*/_inbox/*.md` paths. Claude reads each pending inbox file, decides whether to create a new wiki page or enrich an existing one, writes the result, runs `verify-wiki.py`, deletes the inbox file, and commits. A final push step rebases against `main` to avoid non-fast-forward failures.

**Trigger paths:**
- `AI/_inbox/**`, `Cloud/_inbox/**`, `Data/_inbox/**`, `Engineering/_inbox/**`, `Homelab/_inbox/**`
- `projects/**/_inbox/**`
- `agents-shared/_inbox/**`
- Also `workflow_dispatch` (manual trigger)

Full YAML is at [`templates/workflows/vault-ingest.yml`](templates/workflows/vault-ingest.yml).

**What the Claude prompt instructs, per inbox file:**
1. Read the inbox file.
2. Determine destination type from path: domain wiki for `AI/`, `Cloud/`, `Data/`, `Engineering/`, `Homelab/` prefixes; `projects/{repo}/context.md` or `patterns.md` for `projects/**/_inbox/`; `agents-shared/patterns.md` or `mistakes.md` for `agents-shared/_inbox/`.
3. For domain wiki: new page (full schema) or enrich existing (bump `source_count`, extend body, add links).
4. Wire bidirectional links, update category `_INDEX.md`, cross-reference the 5 most related existing pages.
5. Run `verify-wiki.py` — if errors, commit partial changes and open a GitHub issue; if clean, continue.
6. Delete the inbox file; commit with `ingest: {title}`.

**Guard condition:**
```yaml
if: "!startsWith(github.event.head_commit.message, 'ingest:')"
```
This prevents vault-ingest from re-triggering on its own commits. The guard is **commit-message-based, not actor-based** — deliberately. luminary-scan also pushes as `github-actions[bot]`, so an actor-based guard would block its `scan(...)` commits from reaching vault-ingest. The commit-message guard allows those through while still blocking the `ingest:` commits vault-ingest itself produces.

**Required permissions:** `contents: write`, `issues: write`, `id-token: write`.

**Required secret:** `CLAUDE_CODE_OAUTH_TOKEN`.

### luminary-scan Action

Runs nightly and searches for content authored by 43 tracked luminaries across six sources: X/Twitter, personal blogs, Hacker News, arXiv, Papers With Code, HuggingFace. Only content the luminary wrote themselves, published yesterday, and that passes a novelty filter is captured. Passing content is written to the appropriate domain inbox where vault-ingest picks it up.

**Schedule:** `0 23 * * *` — 23:00 UTC (midnight CET). Also `workflow_dispatch` for manual runs.

Full YAML is at [`templates/workflows/luminary-scan.yml`](templates/workflows/luminary-scan.yml). Luminaries roster is at [`templates/luminaries.json`](templates/luminaries.json).

**Per-luminary Claude prompt, in order:**
1. **Setup** — read `luminary-scan/luminaries.json` and `luminary-scan/seen-urls.json`.
2. **Search** — find content authored by the luminary and published yesterday across the six sources. X/Twitter uses `from:{handle} since:{date}`; HN requires score ≥ 200; blog is fetched if `blog_url` is not null.
3. **Filter** — skip URLs already in `seen-urls.json`; skip if publication date isn't yesterday; skip reposts, pure product announcements, marketing.
4. **Judge novelty** — run `grep -ril '<concept-keywords>' . --include='*.md'` against the vault. 3+ strong matches = skip (already well-covered). 1–2 partial = enrichment candidate. 0 matches = new concept.
5. **Capture** — determine domain, research the concept, write an inbox file to `{Domain}/_inbox/YYYY-MM-DD-{slug}-{concept-slug}.md` using the prescribed format.
6. **After each luminary** — append captured URLs to `seen-urls.json`, stage only that luminary's files, commit `scan({slug}): {summary}`, then immediately `git pull --rebase && git push`.

**The four novelty filters:**
- **Authorship** — content must be written by the luminary, not merely about them. Prevents accumulating secondary commentary.
- **Date** — published yesterday only. Old content recirculates constantly via aggregators; anchoring on a 24-hour window prevents known content re-entering the pipeline.
- **HN score ≥ 200** — filters out low-engagement posts.
- **Grep-before-capture** — 3+ matches means the vault already covers the topic; re-ingesting adds noise.

**Per-luminary push cadence.** Results are committed and pushed after each luminary — not accumulated into one batch. vault-ingest uses `find` to locate inbox files currently present (not a git diff), so accumulation wouldn't break correctness, but batching would cram up to 43 inbox files into a single triggered ingest run (risking timeout and producing one opaque commit). Per-luminary push means:
- vault-ingest processes each luminary's content in its own triggered run with clean scope.
- A failure on one luminary doesn't affect the others.
- Commit history attributes each capture to the specific luminary (`scan(karpathy): ...`, `scan(lecun): ...`).

The "Push any remaining commits" step at the end of the Action is a safety net for commits Claude produced but couldn't push due to transient errors.

**`luminaries.json` schema:**

```json
{
  "name": "Full Name",
  "slug": "url-safe-slug",
  "twitter_handle": "handle_without_at",
  "blog_url": "https://... or null",
  "focus": "brief description of their domain focus"
}
```

- `slug` is used in inbox filenames and commit messages (must be URL-safe).
- `twitter_handle` is without the `@`.
- `blog_url` can be `null`.
- `focus` should be specific — "neural nets, LLM tooling, engineering practice" gives Claude more signal than "AI researcher".

**Guard condition:**
```yaml
if: github.actor != 'github-actions[bot]'
```
Prevents luminary-scan from re-triggering on its own pushes. Contrast with vault-ingest's message-based guard:

| Action | Guard type | Allows through | Blocks |
|---|---|---|---|
| luminary-scan | Actor-based | Human pushes, `workflow_dispatch` | Bot's own per-luminary pushes |
| vault-ingest | Commit-message-based | Bot pushes with `scan(...)` commits | Bot's own `ingest:` wiki-update commits |

This asymmetry is required: luminary-scan pushes under `github-actions[bot]` and must trigger vault-ingest downstream; vault-ingest must not re-trigger itself on its own wiki commits.

**Required secrets:**
- **`CLAUDE_CODE_OAUTH_TOKEN`** — OAuth token for `claude -p` invocations.
- **`VAULT_PAT`** — GitHub PAT with `contents: write` scope, used in the checkout step.

**Why `VAULT_PAT` and not `GITHUB_TOKEN`:** `GITHUB_TOKEN` does not trigger further workflow runs — GitHub deliberately restricts it this way to prevent Action cascades. Each per-luminary push must trigger vault-ingest downstream; that cascade is the entire point of the per-luminary push cadence. A PAT authenticates as the token owner and does trigger further workflows. Using `GITHUB_TOKEN` here would silently break the cascade: luminary-scan completes, pushes land, but vault-ingest never fires. **This is the single most critical secret configuration detail in the system.**

### Agent memory system

The vault stores agent knowledge that would otherwise be lost between sessions. When a Claude session ends, architectural decisions, tricky tradeoffs, and bugs that took an hour to track down disappear from context. The agent memory system captures that knowledge to disk and replays it at the start of the next session — across repo boundaries.

```
projects/{repo-name}/
  context.md         — architectural decisions and tradeoffs for this repo
  patterns.md        — conventions and preferred patterns
  _inbox/

agents-shared/
  INDEX.md           — read at every session start (all repos)
  patterns.md        — cross-repo conventions
  mistakes.md        — bugs and gotchas to avoid
  _inbox/

lessons-learned/{domain}/
  {lesson-title}.md
```

**Session capture.** "capture this to the vault" — Claude determines the right destination, writes a markdown summary, commits, and pushes. vault-ingest fires and updates the right file (creating it if it does not yet exist).

**Session start.** Claude reads `agents-shared/INDEX.md` automatically, without being asked. If `projects/{this-repo}/context.md` exists, it is also read. Both reads happen at the start of every session in every repository, specified in the global `~/.claude/CLAUDE.md`.

**Auto-flag conditions (proactive capture suggestions):**
1. A novel technology stack not yet in the wiki has been discussed in depth.
2. A non-obvious tradeoff took significant reasoning to resolve.
3. A bug's root cause wasn't documented in any source.
4. An architectural decision has a "why" not visible in the code.

**`agents-shared/INDEX.md`** is the single most load-bearing file in the memory system. It is loaded at every session start regardless of which repo is active. It contains a table of files (one-line purpose per file) plus a **Key Entries** section summarising the most important patterns and mistakes — so Claude can act on `INDEX.md` alone without reading the full files. Keep it current as `patterns.md` and `mistakes.md` grow.

### CLAUDE.md conventions

Three-layer architecture — each file fires in a different scope, and together they give Claude complete vault awareness wherever it works:

| File | Scope | Contains |
|------|-------|---------|
| `~/.claude/CLAUDE.md` | Global — every repo | Session-start instructions, vault capture workflow, auto-flag heuristics |
| `knowledge-vault/CLAUDE.md` | Vault repo only | Wiki schema, ingestion rules, bidirectional link rule, YAML warning |
| `{any-other-repo}/CLAUDE.md` | That repo only | Project context, domain hints, project-specific capture heuristics |

**Global `~/.claude/CLAUDE.md` blocks:**
- **Session-start instructions** (run automatically): `git pull` the vault, read `agents-shared/INDEX.md`, read `projects/{this-repo}/context.md` if it exists.
- **Capture workflow** — how to determine the right inbox, the commit message convention (`capture: {title}`), the push sequence that triggers vault-ingest.
- **Auto-flag heuristics** — the four capture trigger conditions.
- **Bootstrap instructions** — how to initialise a new repo in the vault (read README + key architecture files, draft `context.md` and `patterns.md`, present for review, commit).

A starting-point template is at [`templates/global-claude.md`](templates/global-claude.md). Replace the placeholder `/path/to/your-vault` with your vault path and `your-github-username/your-vault-repo` with your remote.

**Vault `knowledge-vault/CLAUDE.md` blocks** (mirrored in [`templates/CLAUDE.md`](templates/CLAUDE.md)):
- graphify integration rules (read `GRAPH_REPORT.md` before architecture questions).
- Full wiki page schema — all frontmatter fields, valid `type` values by domain, required body sections.
- Inbox ingestion workflow — step-by-step.
- YAML editing warning.
- Agent memory system structure and session capture workflow.
- References/ rules — what belongs there, what must never be touched during ingestion.

**Per-repo `{any-other-repo}/CLAUDE.md` blocks** (optional but recommended for any repo you work in regularly):
- **Project context** — what this repo is, its primary domain(s), what kinds of concepts emerge from sessions here. This supplements the `projects/{repo}/context.md` that Claude reads from the vault at session start.
- **Domain classification hint** — which vault domain new captures from this repo typically belong to (e.g. "new concepts from this repo go to `Engineering/_inbox/`"). Prevents Claude from having to guess.
- **Inbox schema reminder** — the vault's `CLAUDE.md` holds the full inbox frontmatter schema, but that file is only loaded when Claude is working *inside* the vault repo. A per-repo `CLAUDE.md` can either include the schema inline or instruct Claude to read it from the vault before writing any inbox file.
- **Project-specific capture heuristics** — in addition to the global auto-flag conditions, any patterns specific to this repo that should trigger a vault capture (e.g. "whenever we discuss a new API design pattern, suggest capturing to `Engineering/_inbox/`").

The global `CLAUDE.md` makes Claude vault-aware everywhere. The vault `CLAUDE.md` makes Claude know how to write correctly inside the vault. The per-repo `CLAUDE.md` gives Claude the project context it needs to aim captures accurately without being prompted.

**`/vault` skill** (`~/.claude/skills/vault/SKILL.md`, template at [`templates/vault-skill.md`](templates/vault-skill.md)): a companion skill for explicit vault operations. Invoke it when you want step-by-step guidance rather than relying on the always-on CLAUDE.md rules:

| Sub-command | Does |
|---|---|
| `/vault capture [concept]` | Write inbox file with correct schema, commit, push |
| `/vault compile <path-or-url>` | Turn a raw note into a full wiki page end-to-end |
| `/vault extract <reference-path>` | Propose + generate inbox files from a reference doc |
| `/vault bootstrap` | Draft `context.md` + `patterns.md` for current repo |
| `/vault verify` | Run `verify-wiki.py` and fix every error class |

The skill is self-contained — it includes the inbox and wiki schemas inline, so it works in any repo session regardless of which CLAUDE.md files are loaded.

**The principle:** instructions live in `CLAUDE.md`, not in per-session prompts. A Claude session with a complete `CLAUDE.md` produces schema-compliant wiki pages without being told the schema. If you find yourself repeatedly telling Claude the same thing at the start of a session, that instruction belongs in `CLAUDE.md`.

### /vault skill

A Claude Code skill that provides guided, step-by-step workflows for all vault operations. Where the three CLAUDE.md files give Claude always-on context and rules, the `/vault` skill is invoked explicitly when you want structured assistance — checklists, review gates, and schema references — for a specific operation.

**Install:** copy [`templates/vault-skill.md`](templates/vault-skill.md) to `~/.claude/skills/vault/SKILL.md`. The skill is then available as `/vault` in any Claude Code session.

**Usage:** `/vault` with no argument shows the menu. With a sub-command, it routes directly to that workflow.

---

#### `/vault capture [concept]`

Write a single well-formed inbox file for a concept, session finding, or architectural decision, then commit and push so vault-ingest fires.

The skill determines the right destination (domain inbox, per-repo inbox, or agents-shared), writes the inbox file using the correct schema, and commits with the `capture: {title}` convention.

```
/vault capture "chain-of-thought prompting"
/vault capture "JWT refresh token rotation — architectural decision for auth-service"
/vault capture "discovered race condition in task queue — cross-repo gotcha"
```

---

#### `/vault compile <path-or-url>`

Turn a raw note file or URL into a complete wiki page end-to-end: reads the source, judges new page vs enrichment, writes the full frontmatter + body, wires bidirectional links, updates the category `_INDEX.md`, reads the 5 most related existing pages for cross-references, runs `verify-wiki.py`, and deletes the source file.

```
/vault compile AI/_inbox/2026-04-26-rag-notes.md
/vault compile https://example.com/paper-on-rlhf
```

---

#### `/vault extract <reference-path>`

Survey a reference document, propose a numbered list of concepts worth promoting to wiki pages (both new concepts and enrichments of existing pages), stop for your approval, then generate one inbox file per approved concept. The reference doc is never modified.

```
/vault extract References/aws-saa-notes.md
/vault extract References/Architecture/event-driven-design.md
```

Example interaction after invocation:

```
Concepts found in References/aws-saa-notes.md:

New pages:
  1. VPC Endpoint — private AWS service access without internet routing → Cloud/_inbox/
  2. Placement Groups — EC2 instance clustering for latency/throughput → Cloud/_inbox/

Enrichments (adds depth to existing pages):
  3. Auto Scaling — adds cold start behaviour detail → enriches [[Auto Scaling]] → Cloud/_inbox/

Skipped (already well-covered):
  - IAM Roles — mature page, 4 sources

Reply with numbers (e.g. "1 3"), "all", or "none".
```

Replying `1 2` generates two inbox files in `Cloud/_inbox/`, commits, and pushes. vault-ingest compiles each into a wiki page. Replying `3` generates an enrichment inbox file; vault-ingest opens the existing `[[Auto Scaling]]` page and adds the new detail rather than creating a duplicate.

---

#### `/vault bootstrap`

Read the current repo's README, CLAUDE.md, recent git log, and key architecture files, then draft `projects/{repo}/context.md` (decisions and tradeoffs) and `projects/{repo}/patterns.md` (conventions and gotchas) in the vault. Stops for your review before committing.

```
/vault bootstrap
```

---

#### `/vault verify`

Run `scripts/verify-wiki.py` against the vault, parse the output by error class (missing fields, invalid type, broken wikilinks, missing reciprocals, missing sections), fix each systematically, re-run until clean, then commit.

```
/vault verify
```

---

### verify-wiki.py

The vault's integrity checker. Walks every `domain/category/` subdirectory and validates each wiki page against the full schema.

**What it checks:**
- **Frontmatter completeness** — all required fields present.
- **Type validity** — `type` must be valid for the page's domain.
- **Status validity** — `status` must be `stub`, `draft`, or `mature`.
- **source_count integrity** — must be an integer.
- **Wikilink resolution** — every wikilink in `related:`, `builds_on:`, `contrasts_with:`, `appears_in:` must resolve to a real wiki page.
- **Bidirectional reciprocal** — every `related:` entry must be reciprocated. `builds_on:` and `contrasts_with:` are one-directional and not checked.
- **Required body sections** — all four headings must be present, literal string match.

**When to run:** after every batch of wiki page writes, before committing. `vault-ingest` runs it automatically after every ingestion cycle.

**Output format:**

```
OK — N pages passed all checks.
```

or one line per violation:

```
AI/concepts/Large Language Model.md: missing field 'source_count'
AI/concepts/RAG.md: related '[[Embeddings]]' not reciprocated in target
Cloud/services/Azure OpenAI.md: type 'concept' invalid for domain 'Cloud'
```

**How vault-ingest uses it:** if errors are reported, vault-ingest commits partial changes and opens a GitHub issue titled `"Vault ingest errors: {inbox file}"` listing the specific failures. This surfaces errors for manual review rather than letting bad state accumulate.

**Location:** `scripts/verify-wiki.py` in the vault root. It hardcodes the domain names and valid category/type mappings for this particular vault layout — if you replicate with different domains, edit those mappings. For this reason it is not a template to copy unchanged.

---

## Replicate this

> **Environment note:** This system was built on WSL2 (Ubuntu) under Windows 11. Steps are written for that environment. Most steps work identically on native Linux and macOS — platform-specific differences are noted where they exist.

### Prerequisites

**GitHub repository.** A standard git repository pushed to GitHub. Both Actions push commits back to the repo, so they need `contents: write` permission — declared at the top of each workflow YAML; GitHub-hosted runners honour it automatically. If you run on self-hosted runners or another CI platform, adapt the checkout and push steps.

**SSH key for GitHub.** Obsidian Git pushes via SSH. You need an SSH key registered with GitHub before the plugin can authenticate. If you do not already have one:

```bash
ssh-keygen -t ed25519 -C "your@email.com"
# Accept default path ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub
```

Add the public key to **GitHub → Settings → SSH and GPG keys → New SSH key**. Then clone (or switch) your vault to the SSH remote:

```bash
git clone git@github.com:your-username/your-vault.git
# or, to switch an existing clone:
git remote set-url origin git@github.com:your-username/your-vault.git
```

Obsidian Git uses the default SSH agent. On Windows, ensure the key is loaded (`ssh-add ~/.ssh/id_ed25519`) or use Pageant. On macOS/Linux this is typically automatic.

**Obsidian Git plugin.** Install via: Obsidian → Settings → Community plugins → Browse → search "Obsidian Git" → Install → Enable. Configuration used:
- **Auto-pull on startup**: enabled
- **Auto-push after file change**: enabled (or a short commit interval)
- **Commit message**: `vault backup: {{date}}`

Obsidian Git is one of two trigger mechanisms for `vault-ingest` — the other is `luminary-scan`, which pushes inbox files automatically after each nightly scan. For manual captures: drop a file into `_inbox/` → Obsidian Git commits and pushes → GitHub sees the push → `vault-ingest` fires. Without auto-push, manually dropped inbox files sit locally and nothing happens.

**Claude Code CLI subscription.** Install with the native installer (auto-updates in the background):

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Alternatives: `brew install --cask claude-code` on macOS, or `winget install Anthropic.ClaudeCode` on Windows native. `npm install -g @anthropic-ai/claude-code` works but does not auto-update and is not the recommended local install. (The Actions use npm internally because it is simpler in CI — separate from your local install.)

Both Actions invoke `claude -p` (headless/non-interactive) and authenticate via the `CLAUDE_CODE_OAUTH_TOKEN` secret. This is a **Claude Code subscription token**, not a raw Anthropic API key from console.anthropic.com:

- A subscription token covers Action runs with no additional per-token cost.
- A raw API key would incur per-token charges on every Action run (see **Costs** below).

**How to get the token:** run `claude setup-token` in your terminal (or follow the prompts from `/install-github-app` if you are inside an active Claude Code session). The flow opens a browser, asks you to approve the GitHub App, then takes you to an Anthropic URL where the token is generated. Copy it and paste it back into the CLI, then add that same token as the `CLAUDE_CODE_OAUTH_TOKEN` repository secret. Requires a Pro, Max, Team, or Enterprise Claude subscription.

**Required GitHub secrets:**

| Secret | Used by | What it is |
|--------|---------|------------|
| `CLAUDE_CODE_OAUTH_TOKEN` | Both Actions | Claude Code OAuth token from your Claude account |
| `VAULT_PAT` | luminary-scan only | GitHub PAT with `contents: write` scope |

Add via: GitHub repository → Settings → Secrets and variables → Actions → New repository secret.

### Day-0 walkthrough

These steps take you from an empty vault to a fully operational system. Work through them in order — each depends on the previous.

Before you begin, clone this repo so [`templates/`](templates/) is available locally:

```bash
git clone https://github.com/corticalstack/knowledge-vault-ops
```

Steps 4, 6, 8, and 9 run **from your vault root**. All other steps run from wherever is convenient.

1. **Install graphify:**
   ```bash
   pip install graphifyy
   ```

2. **Run graphify over your vault:**
   ```bash
   graphify /path/to/vault
   ```
   Produces `graphify-out/` containing `GRAPH_REPORT.md`, `graph.html`, `graph.json`.

3. **Copy `CLAUDE.md` to vault root before running the reorganisation prompt:** copy [`templates/CLAUDE.md`](templates/CLAUDE.md) into your vault repository root now — the reorganise prompt's Phase 3 will update the `Valid types:` line it contains in place, and doing this here means the full schema and inbox-workflow context is available to Claude from the first session onward. If you want a home for long-form hand-authored knowledge assets (architecture notes, exam study material, playbooks) that must survive verbatim and never be ingested, also create `References/` at the vault root and copy [`templates/references-index.md`](templates/references-index.md) to `References/_INDEX.md`.

4. **Run the reorganisation prompt.** Commit your vault first so the moves are diff-able. From vault root, paste the prompt from [`templates/day-zero-reorganise-prompt.md`](templates/day-zero-reorganise-prompt.md) into a Claude Code session. The prompt runs in three phases, each stopping for your review: Phase 1 rolls graphify's 50–100 fine-grained communities up into a small set of top-level domains AND derives a per-domain category type starter list from graphify's node-ID prefixes, writes `domain-proposal.md`, and stops — edit it to rename / merge / split domains or drop thin category types before replying `proceed`. Phase 2 classifies every loose note against the approved domains, writes `reorganise-plan.md`, and stops — edit any row before replying `apply`. Phase 3 writes the derived `Valid types:` line into vault `CLAUDE.md`, creates the domain folders (plus `_inbox/` subfolders), and `git mv`s every planned file. Category subfolders (`concepts/`, `models/`, etc.) are not created here — they emerge during wiki compilation.

5. **Create `.base` files per domain** (optional but recommended): `wiki-recent.base`, `wiki-stubs.base`, `wiki-mature.base`, `wiki-review.base`. Reference copies are in [corticalstack/knowledge-vault/tree/main/AI](https://github.com/corticalstack/knowledge-vault/tree/main/AI) — these define the Obsidian Bases views.

6. **Run `add_frontmatter.py`.** Must run *after* step 4 — the script derives `domain:` from the top-level folder path, so every note has to live under its domain folder before it runs, or every stamp will be `domain: Unknown`. From the `knowledge-vault-ops` clone, copy the script into your vault, then run from vault root:
   ```bash
   cp templates/add_frontmatter.py /path/to/your-vault/docs/scripts/add_frontmatter.py
   # From vault root:
   python docs/scripts/add_frontmatter.py              # dry run
   python docs/scripts/add_frontmatter.py --apply      # apply
   ```
   Stamps every note with the standard frontmatter schema that vault-ingest and the wiki schema depend on.

7. **Begin wiki compilation.** Use Claude with `GRAPH_REPORT.md` as context. Start from [`templates/wiki-page.md`](templates/wiki-page.md). Work domain by domain, not whole vault at once. Category subfolders (`AI/concepts/`, `AI/techniques/`, etc.) are created as notes are compiled — Claude places each page under the folder matching its `type:` value, constrained by the `Valid types:` line the reorganise prompt seeded into `CLAUDE.md` from graphify's node-ID prefixes.

8. **Run the category finalisation prompt.** Once you have a representative sample of pages in each domain (ideally ≥3 per intended category), paste [`templates/day-zero-categories-prompt.md`](templates/day-zero-categories-prompt.md) into a Claude Code session from vault root. The prompt runs in two phases: Phase 1 observes what category folders emerged and proposes a final list, writing `categories-proposal.md`. Phase 2 (after you reply `apply`) rewrites the `Valid types:` line in vault `CLAUDE.md` and the `DOMAINS` dict in `scripts/verify-wiki.py` to match. Both files enforce the category list — do this before regular `vault-ingest` operation begins or new pages will land in nonexistent folders.

9. **Run `verify-wiki.py` after each batch** (from vault root — the script is vault-specific and lives in the vault, not in this repo):
   ```bash
   python3 scripts/verify-wiki.py
   ```
   Fix all errors before committing.

10. **Add global `CLAUDE.md` blocks** to your `~/.claude/CLAUDE.md`. Start from [`templates/global-claude.md`](templates/global-claude.md) — replace `/path/to/your-vault` with your vault path and `your-github-username/your-vault-repo` with your remote (see **CLAUDE.md conventions** above). For any other repos where you want Claude to capture to the vault, drop a personalised copy of [`templates/per-repo-claude.md`](templates/per-repo-claude.md) into that repo's root.

11. **Copy workflow YAMLs:** copy [`templates/workflows/*`](templates/workflows/) to `.github/workflows/` in your vault repository.

12. **Add GitHub secrets:** add `CLAUDE_CODE_OAUTH_TOKEN` and `VAULT_PAT` to your vault repository (see **Prerequisites** above).

13. **Initialise luminary-scan files:** copy [`templates/luminaries.json`](templates/luminaries.json) to `luminary-scan/luminaries.json` in your vault, edit to match your focus areas, then create an empty `seen-urls.json`:
    ```bash
    echo '[]' > luminary-scan/seen-urls.json
    ```
    Commit and push both. The Action will fail if either is missing.

14. **Test vault-ingest:** drop a `.md` file into any `_inbox/` folder, commit and push (Obsidian Git does this automatically if auto-push is enabled), then watch the Action run. The test passes when the inbox file has been deleted and a new wiki page appears in a commit starting with `ingest:`.

15. **Test luminary-scan:** trigger manually via Actions tab → "Luminary Scan" → Run workflow. After it completes, commits starting with `scan({slug}):` should appear. Any captured content will trigger vault-ingest automatically per-luminary — check the Actions tab for vault-ingest runs that followed the scan immediately.

### Configuration — what to personalise

Everything else can be copied verbatim from [`templates/`](templates/).

**Domain map.** If your vault uses different domains from the default (AI, Cloud, Data, Engineering, Homelab), update these in sync:
1. Top-level folder names in your vault.
2. `vault-ingest.yml` trigger paths — the `on.push.paths` list watches specific `_inbox/**` paths. Replace `AI/_inbox/**` etc. with your equivalents.
3. `DOMAIN_MAP` in `add_frontmatter.py` — maps domain folder names to the `domain:` frontmatter value.
4. Vault `CLAUDE.md` valid domain list — used when classifying inbox files.
5. Run graphify first to discover your vault's natural clusters before committing to domain names.

**Luminaries roster.** Start from [`templates/luminaries.json`](templates/luminaries.json). Edit to match your focus areas:
- **Remove** luminaries outside your interests — each one adds scan time and cost.
- **Add** entries using the schema: `name`, `slug`, `twitter_handle`, `blog_url`, `focus`.
- The **`focus` field** is passed to Claude as context when classifying captured content — be specific.
- Keep the file at `luminary-scan/luminaries.json` in your vault root.

**Cron schedule.** Default: `0 23 * * *` (23:00 UTC daily). Edit the `cron:` line in `luminary-scan.yml`. **Sizing note:** each luminary scan takes 1–3 minutes. At 43 luminaries, a full run can take up to 130 minutes. The Action has `timeout-minutes: 60` — with the default roster it will typically be killed mid-scan. Raise `timeout-minutes` or trim your roster.

**Vault path in global `CLAUDE.md`.** Replace `/mnt/c/Users/jonpaulboyd/Documents/knowledge-vault` with your vault path in your `~/.claude/CLAUDE.md`. Also replace `corticalstack/knowledge-vault` with your GitHub remote.

**Working across multiple machines.** The vault works on as many machines as you like — GitHub is the single source of truth, each machine is just a working copy.

What each machine needs:
- A local clone of the vault repo at whatever path suits that machine: `git clone git@github.com:you/knowledge-vault /path/to/vault`
- Its own `~/.claude/CLAUDE.md` from [`templates/global-claude.md`](templates/global-claude.md) with that machine's local vault path — this is the only thing that differs between machines
- Claude Code installed
- `~/.claude/skills/vault/SKILL.md` copied from [`templates/vault-skill.md`](templates/vault-skill.md)
- Git configured with SSH access to the GitHub repo

How sync works: every session starts with `git pull --ff-only --quiet` so whichever machine you pick up on, it's current before any work begins. Every capture commits and pushes to GitHub; vault-ingest compiles on GitHub and pushes the wiki page back; the next pull on any machine brings it down.

Remote servers (no Obsidian): the vault works identically over SSH — captures commit and push the same way, vault-ingest fires on GitHub. You just won't have the Obsidian graph view. Clone the repo, set up `~/.claude/CLAUDE.md` with the server-side path, and all `/vault` sub-commands work as normal.

**seen-urls.json.** Initialise as an empty JSON array at `luminary-scan/seen-urls.json`. The Action reads and appends after each luminary.

### Costs

**Claude Code subscription.** If you have one, Action runs are covered — no additional per-token cost. This is the approach used here and the reason `CLAUDE_CODE_OAUTH_TOKEN` is the required secret.

**Raw API key alternative.** If you don't have a subscription, replace `claude -p` with direct Anthropic API calls. Rough estimates at current pricing:
- **vault-ingest, single inbox file**: ~$0.01–$0.05 per run.
- **luminary-scan with 43 luminaries**: ~$1–$3 per nightly run.

At those rates, a heavily used vault (daily ingest + nightly scan) runs roughly $30–$100/month on raw API. A subscription is more economical if you're already using the CLI for other work.

**GitHub Actions runner minutes.** Both Actions run on `ubuntu-latest`. The free tier is 2,000 minutes/month (same for public and private on the free plan). Typical runtimes:
- **vault-ingest**: 2–5 minutes per run.
- **luminary-scan**: up to 60 minutes (`timeout-minutes: 60`).

A vault with 1–2 inbox drops per day plus one nightly scan uses ~90–120 minutes/month — well within the free tier. Recalculate if you expand the roster significantly or trigger vault-ingest many times per day.

**Storage.** The vault grows continuously. GitHub's soft repo limit is 1 GB — a text-only vault with hundreds of wiki pages stays well under this for years.

---

## Templates

[`templates/`](templates/) mirrors live files from the source vault. Before updating any template, read the corresponding live file first, then overwrite the template to match.

| Template file | Source | Purpose |
|---------------|--------|---------|
| [`templates/vault-skill.md`](templates/vault-skill.md) | `~/.claude/skills/vault/SKILL.md` | `/vault` skill — capture, compile, extract, bootstrap, verify sub-commands |
| [`templates/global-claude.md`](templates/global-claude.md) | `~/.claude/CLAUDE.md` | Starting-point for the global file — replace vault path and GitHub remote |
| [`templates/CLAUDE.md`](templates/CLAUDE.md) | vault `CLAUDE.md` | Drop into vault root — schema + ingestion rules for Claude |
| [`templates/per-repo-claude.md`](templates/per-repo-claude.md) | `{repo}/CLAUDE.md` | Per-repo template — project context, domain hint, inline inbox schema |
| [`templates/wiki-page.md`](templates/wiki-page.md) | vault `Templates/wiki-page.md` | Starting template for new wiki pages |
| [`templates/inbox-entry.md`](templates/inbox-entry.md) | n/a (manual) | Canonical inbox file format for manual captures |
| [`templates/references-index.md`](templates/references-index.md) | n/a (built for this repo) | `_INDEX.md` drop-in for vault's `References/` folder (persistent knowledge assets, never ingested) |
| [`templates/day-zero-reorganise-prompt.md`](templates/day-zero-reorganise-prompt.md) | n/a (built for this repo) | Day-0 prompt to reorganise a flat vault into top-level domain folders |
| [`templates/day-zero-categories-prompt.md`](templates/day-zero-categories-prompt.md) | n/a (built for this repo) | Day-0 prompt to finalise per-domain category taxonomy into `CLAUDE.md` and `verify-wiki.py` |
| [`templates/add_frontmatter.py`](templates/add_frontmatter.py) | vault `docs/scripts/add_frontmatter.py` | Day-0 frontmatter stamping script |
| [`templates/luminaries.json`](templates/luminaries.json) | vault `luminary-scan/luminaries.json` | 43-entry luminary roster (edit to taste) |
| [`templates/workflows/vault-ingest.yml`](templates/workflows/vault-ingest.yml) | vault `.github/workflows/vault-ingest.yml` | Drop into `.github/workflows/` in your vault |
| [`templates/workflows/luminary-scan.yml`](templates/workflows/luminary-scan.yml) | vault `.github/workflows/luminary-scan.yml` | Drop into `.github/workflows/` in your vault |
