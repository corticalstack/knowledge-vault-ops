## graphify

> Only add this block if you have run graphify on your vault (see [quick-start](../docs/setup/quick-start.md) steps 1–2). Delete this section if you have not run graphify yet.

This project has a graphify knowledge graph at graphify-out/.
The pip package name is **`graphifyy`** (double y): `pip install graphifyy --break-system-packages`
Invoke via the `/graphify` skill in Claude Code — the skill handles installation automatically.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- After modifying code files in this session, run `python3 -c "from graphify.watch import _rebuild_code; from pathlib import Path; _rebuild_code(Path('.'))"` to keep the graph current

## LLM Wiki

This vault has a structured wiki across 5 domains: AI, Cloud, Data, Engineering, Homelab.
- **Wiki pages** in domain/category subdirectories (e.g. `AI/concepts/`, `Cloud/services/`)
- **Integrity tool:** `python3 scripts/verify-wiki.py` — run after every batch of writes; checks frontmatter, broken wikilinks, bidirectional reciprocals, required sections
- **Vault index:** `_INDEX.md` — cross-domain map and bridge concepts

### Wiki page schema (required frontmatter)

```yaml
---
title: Page Title
aliases: []
tags:
- Domain/category
type: <see valid types below>
domain: <AI|Cloud|Data|Engineering|Homelab>
status: <stub|draft|mature>   # stub=source_count≤1, draft=2, mature=≥3
source_count: <int>
created: YYYY-MM-DD
updated: YYYY-MM-DD
related:
- '[[Other Page]]'
builds_on:
- '[[Other Page]]'
contrasts_with: []
appears_in: []
# Extended fields (optional — added by luminary-scan Action):
# origin: luminary-scan     # present on pages auto-seeded by the nightly scan
# luminary: Name            # triggering luminary; list if multiple enriched the page
---
```

Valid types: AI → concept/model/technique/tool · Cloud → service/pattern/architecture · Data → concept/algorithm/workflow/tool · Engineering → practice/tool/pattern · Homelab → hardware/os/service

Required body sections (exact text): `## How It Works` · `## Tensions & Open Questions` · `## See Also` · `## Sources`

**Bidirectional reciprocal rule:** every entry in `related:` must appear in the target page's `related:` too. verify-wiki.py enforces this.

### Integrating a new source (inbox workflow)

When the user drops a file into `<Domain>/_inbox/` or asks you to integrate a URL/document:

1. **Read the source** — fetch the URL or read the file
2. **Decide: new page or enrich existing?**
   - New concept not yet in the wiki → create a new page in the right `Domain/category/` directory
   - Adds depth to an existing page → edit that page (bump `source_count`, extend body, add links)
3. **Write the wiki page** with the full schema above. Use existing pages as style reference (e.g. `AI/concepts/Large Language Model.md`)
4. **Wire bidirectional links** — every page in `related:` must link back. Add reciprocals to target pages
5. **Update the category `_INDEX.md`** — add the new page to the "All Pages" list, the relevant section (Foundational/Secondary/etc.), and the "How These Concepts Relate" prose if the page has meaningful connections
6. **Run `python3 scripts/verify-wiki.py`** — fix all reported issues before committing
7. **Delete the source file from `_inbox/`** — the URL/citation lives in `## Sources` on the wiki page. Do not move to `processed/`; keeping raw source copies creates duplicate search results in Obsidian.
7. **Optionally run `/graphify <Domain>/ --update`** to pull the new page into the graph

### YAML editing warning

**Never use yaml.safe_load → re-serialize to edit frontmatter.** It corrupts `builds_on`/`appears_in` lists and breaks the frontmatter. Use raw text / regex manipulation only, or the Edit tool for targeted field changes.

## Agent Memory System

The vault also stores **agent knowledge** — architectural decisions, cross-repo
patterns, lessons learned, and domain concepts discovered during Claude Code sessions.

### New directories

- `projects/{repo-name}/` — per-repo context: `context.md` (decisions/tradeoffs) and `patterns.md` (conventions/patterns). Each has a `_inbox/` for session captures.
- `agents-shared/` — cross-repo patterns (`patterns.md`) and known mistakes (`mistakes.md`). `INDEX.md` is read at every session start.
- `lessons-learned/{domain}/` — one file per lesson, domain-organised (e.g. `graphdb/`, `azure/`).

### Session start (when working in any repo that has vault access)

1. `git -C /path/to/your-vault pull --ff-only --quiet`
2. Read `agents-shared/INDEX.md`
3. If `projects/{this-repo}/context.md` exists, read it
4. For domain-specific work, grep: `grep -rl "{concept}" /path/to/your-vault --include="*.md" | head -5` then read matches

### Capture during sessions

When asked to "capture this to the vault" or when auto-flagging a concept:
1. Determine destination:
   - New concept not in wiki → appropriate domain `_inbox/` (for full wiki ingestion)
   - Architectural decision for current repo → `projects/{repo}/_inbox/`
   - Cross-repo pattern or gotcha → `agents-shared/_inbox/`
2. Write a well-formed markdown summary to that inbox
3. `git -C /path/to/your-vault add -A && git commit -m "capture: {title}" && git push`
4. The `vault-ingest` GitHub Action fires automatically

### Auto-flag heuristics

Proactively surface a capture suggestion when:
- A novel technology stack not yet in the wiki has been discussed in depth
- A non-obvious tradeoff took significant reasoning to resolve
- A bug's root cause wasn't documented in any source
- An architectural decision has a "why" not visible in the code

### Brownfield bootstrap

When asked "Bootstrap this repo in the vault":
1. Read README, CLAUDE.md, `git log --oneline -50`, key architecture files
2. Draft `projects/{repo}/context.md` and `projects/{repo}/patterns.md`
3. Present for review, then commit to vault

### Valid domains (extensible)

Current: **AI · Cloud · Data · Engineering · Homelab**

To add a new domain: create top-level directory + `_INDEX.md` + `_inbox/` + entry
in vault `_INDEX.md` + add to this list. Propose a new domain when a captured
concept fits none of the above.

## References/ — persistent knowledge assets (not a wiki domain)

`References/` at the vault root holds full-fidelity, hand-authored knowledge assets —
extensive architecture notes, exam / certification study material, long-form guides.

**Never touch `References/` during ingestion, compilation, or reorganisation:**
- `vault-ingest` does not fire on it (its path filter is `*/_inbox/**`)
- `verify-wiki.py` does not walk it (only validates `Domain/category/*.md`)
- Day-0 reorganise and category prompts list it under LEAVE UNTOUCHED
- No schema requirements, no frontmatter rules, no section rules — user's structure, user's voice

**When to put content here instead of `_inbox/`:**
- The markdown is itself the deliverable, not capture-material for the wiki
- The doc's linear narrative would be lost if shattered into atomic wiki pages
- The content contains images, tables, diagrams, or code blocks that must survive verbatim

**Cross-linking is fine in both directions:** wiki pages can `[[References/...]]` and
reference docs can `[[Large Language Model]]` wiki pages. Backlinks work as usual.

**Extracting concepts to the wiki:** if a reference doc contains concepts that deserve
wiki pages, create atomic inbox files in the relevant `Domain/_inbox/` with a citation
pointing to the reference doc. The reference doc itself stays intact.
