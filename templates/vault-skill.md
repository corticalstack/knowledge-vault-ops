---
name: vault
description: Work with the knowledge vault — capture concepts, compile notes into wiki pages, extract from reference docs, bootstrap repos, verify integrity
trigger: /vault
---

# /vault

All knowledge vault operations in one skill. The vault path and session-start rules come from your global `~/.claude/CLAUDE.md` — this skill provides the step-by-step workflows for each operation.

## Routing

Infer the operation from how the skill is invoked. If no sub-command is given, show the menu.

| Invocation | Routes to |
|---|---|
| `/vault` | Show menu — ask which operation |
| `/vault capture [concept or description]` | → **Capture** |
| `/vault compile <path-or-url>` | → **Compile** |
| `/vault extract <reference-path>` | → **Extract** |
| `/vault bootstrap` | → **Bootstrap** |
| `/vault verify` | → **Verify** |

---

## Menu (no sub-command given)

Present this and ask the user to choose:

```
/vault — knowledge vault operations

  capture   Write a concept or session finding to the vault inbox
  compile   Turn a raw note or URL into a wiki page
  extract   Pull concepts from a reference doc into the wiki
  bootstrap Initialise this repo's context in the vault
  verify    Run verify-wiki.py and fix all reported errors

Which operation?
```

---

## Operation: capture

Write a well-formed inbox file for a concept, session finding, or architectural decision, then commit and push so vault-ingest fires.

**Step 1 — Determine destination**

| What it is | Destination |
|---|---|
| General concept new to the wiki | `{vault}/{Domain}/_inbox/` |
| Concept that enriches an existing wiki page | `{vault}/{Domain}/_inbox/` (set `capture_type: enrichment`, `enriches: [[Page Name]]`) |
| Architectural decision for the current repo | `{vault}/projects/{repo-name}/_inbox/` |
| Cross-repo pattern or gotcha | `{vault}/agents-shared/_inbox/` |

**Step 2 — Write the inbox file**

Filename: `YYYY-MM-DD-{concept-slug}.md`

For domain wiki inbox files, use this schema exactly:

```yaml
---
sources:
- <url, "session capture", or [[doc-filename]] for vault-internal paths>
luminary: null
date: YYYY-MM-DD
domain: <AI|Cloud|Data|Engineering|Homelab>
capture_type: <new_concept|enrichment>
enriches:          # omit for new_concept; [[Page Name]] for enrichment
origin: manual
---

## Summary

One paragraph — what is this concept / decision / pattern?

## Key Points

- One bullet per distinct, independently useful claim.

## Connections

- [[Existing Wiki Page]] — how this relates

## Source Quote / Key Excerpt

> Paste the most important verbatim extract, or "N/A" for session captures.
```

For `projects/{repo}/_inbox/` or `agents-shared/_inbox/`, use plain markdown — no schema required. Write a clear title, context, the decision or pattern, and the reasoning behind it.

**Step 3 — Commit and push**

```bash
git -C {vault-path} add -A
git -C {vault-path} commit -m "capture: {title}"
git -C {vault-path} push
```

vault-ingest fires automatically on push. Confirm the Action runs in GitHub → Actions.

**Step 4 — Confirm**

Report: filename written, destination, commit message used.

---

## Operation: compile

Turn a raw note file or URL into a full wiki page with the required schema.

**Step 1 — Read the source**

If a path is given, read the file. If a URL is given, fetch it.

**Step 2 — Decide: new page or enrichment?**

- Search the wiki for an existing page on this concept: `grep -ril "{concept}" {vault-path} --include="*.md" | head -5`
- If a page exists → enrichment: edit that page, bump `source_count`, extend body, add links. Skip to step 5.
- If no page exists → new page: continue to step 3.

**Step 3 — Determine domain and category**

- Domain: AI / Cloud / Data / Engineering / Homelab
- Category (type): use the `Valid types:` line from vault `CLAUDE.md`. Common: `concept`, `model`, `technique`, `tool`, `service`, `pattern`, `practice`
- Destination: `{vault}/{Domain}/{category}s/{Page Title}.md`

**Step 4 — Write the wiki page**

Required frontmatter:

```yaml
---
title: "Page Title"
aliases: []
tags:
- Domain/category
type: <concept|model|technique|tool|service|pattern|practice>
domain: <AI|Cloud|Data|Engineering|Homelab>
status: stub          # stub=source_count≤1, draft=2, mature=≥3
source_count: 1
created: YYYY-MM-DD
updated: YYYY-MM-DD
related:
- '[[Related Page]]'
builds_on:
- '[[Foundational Page]]'
contrasts_with: []
appears_in: []
---
```

Required body sections (exact heading text):

```markdown
## How It Works

## Tensions & Open Questions

## See Also

## Sources
```

**Step 5 — Wire bidirectional links**

Every page in `related:` must be edited to add `[[This Page]]` back to its own `related:` list. Check each one and add the reciprocal if missing.

**Step 6 — Update category `_INDEX.md`**

Add the new page to:
- The "All Pages" list
- The relevant section (Foundational / Secondary / etc.)
- The "How These Concepts Relate" prose if the page has meaningful connections

**Step 7 — Read 5 related pages**

Read the 5 most closely related existing wiki pages. Add any cross-references or depth that the new source adds to those pages.

**Step 8 — Verify**

```bash
python3 {vault-path}/scripts/verify-wiki.py
```

Fix every reported error before committing.

**Step 9 — Delete the source file**

If the source was an inbox file, delete it — the citation lives in `## Sources`. Do not move to `processed/`.

**Step 10 — Commit**

```bash
git -C {vault-path} add -A
git -C {vault-path} commit -m "ingest: {page title}"
```

---

## Operation: extract

Scan a reference document, propose a list of concepts worth promoting to wiki pages, then generate one inbox file per approved concept.

The reference doc is **never modified**. It stays exactly as written.

**Step 1 — Read the reference doc**

Read the full file at the given path (e.g. `References/aws-saa-notes.md`).

**Step 2 — Identify extractable concepts**

For each concept found, assess:
- Is it a discrete, self-contained concept (not just a passing mention)?
- Does it already have a wiki page? (`grep -ril "{concept}" {vault-path} --include="*.md" | head -3`)
- If a wiki page exists — is there meaningful new depth the reference adds? → enrichment candidate
- If no wiki page — is it worth a standalone page? → new concept candidate

**Step 3 — Propose and stop for review**

Write a numbered proposal list:

```
Concepts found in {reference-path}:

New pages:
  1. {Concept Name} — {one-line summary} → {Domain}/_inbox/
  2. {Concept Name} — ...

Enrichments (adds depth to existing pages):
  3. {Concept Name} → enriches [[Existing Page]] → {Domain}/_inbox/

Skipped (already well-covered or too thin):
  - {Concept Name} — reason

Reply with the numbers you want captured (e.g. "1 3 5"), or "all", or "none".
```

Stop here and wait for the user's selection.

**Step 4 — Generate inbox files**

For each approved concept, write an inbox file to `{Domain}/_inbox/YYYY-MM-DD-{slug}.md` using the capture schema above. Set `sources: ['[[{doc-filename-without-extension}]]']` and `origin: manual`. Wikilink form (not bare path) so the rendered `## Sources` section in the resulting wiki page is clickable in Obsidian — auto-resolution finds the file by filename anywhere in the vault.

**Step 5 — Commit and push**

```bash
git -C {vault-path} add -A
git -C {vault-path} commit -m "capture: extract from {reference-doc-name} — {N} concepts"
git -C {vault-path} push
```

vault-ingest fires and compiles each inbox file into a wiki page. The reference doc is untouched.

---

## Operation: bootstrap

Initialise this repo's context in the vault so future sessions have architectural memory.

**Step 1 — Read the repo**

Read in order:
1. `README.md` (or root-level docs)
2. `CLAUDE.md` if present
3. `git log --oneline -50`
4. Key architecture files (infer from README or directory structure)

**Step 2 — Draft context.md**

Write a draft for `{vault}/projects/{repo-name}/context.md`:

```markdown
# {Repo Name} — Context

## What this repo does
{one paragraph}

## Architecture decisions
- {Decision}: {rationale}
- {Decision}: {rationale}

## Key tradeoffs
- {Tradeoff}: {why this choice}

## Non-obvious constraints
- {Constraint}: {why it exists}
```

**Step 3 — Draft patterns.md**

Write a draft for `{vault}/projects/{repo-name}/patterns.md`:

```markdown
# {Repo Name} — Patterns

## Conventions
- {Convention}: {description}

## Preferred patterns
- {Pattern}: {when and why}

## Known gotchas
- {Gotcha}: {what to watch for}
```

**Step 4 — Stop for review**

Present both drafts. Ask: "Does this capture the repo accurately? Reply with any corrections before I commit."

**Step 5 — Commit and push**

```bash
git -C {vault-path} add -A
git -C {vault-path} commit -m "bootstrap: {repo-name}"
git -C {vault-path} push
```

---

## Operation: verify

Run the wiki integrity checker and fix every reported error.

**Step 1 — Run**

```bash
python3 {vault-path}/scripts/verify-wiki.py
```

**Step 2 — Parse errors by class**

| Error class | Fix |
|---|---|
| Missing required field | Add the field to frontmatter |
| Invalid `type` | Check the `Valid types:` line in vault CLAUDE.md; correct the type or move the page to the right category folder |
| Invalid `status` | Must be `stub`, `draft`, or `mature` — derive from `source_count`: ≤1 → stub, 2 → draft, ≥3 → mature |
| Broken wikilink | Page was renamed or deleted — update the link or remove it |
| Missing bidirectional reciprocal | Open the target page and add `[[This Page]]` to its `related:` list |
| Missing required section | Add the missing `## Heading` to the page body |

**Step 3 — Re-run after fixes**

```bash
python3 {vault-path}/scripts/verify-wiki.py
```

Repeat until output is clean (no errors reported).

**Step 4 — Commit**

```bash
git -C {vault-path} add -A
git -C {vault-path} commit -m "fix: wiki integrity errors"
```

---

## Reference: inbox schema

```yaml
---
sources:
- <url | "session capture" | '[[doc-filename]]' for vault-internal paths>
luminary: null
date: YYYY-MM-DD
domain: <AI|Cloud|Data|Engineering|Homelab>
capture_type: <new_concept|enrichment>
enriches:          # [[Page Name]] for enrichment; omit for new_concept
origin: <manual|luminary-scan>
---
## Summary
## Key Points
## Connections
## Source Quote / Key Excerpt
```

**Sources format:** vault-internal references (anything under `References/`, `processed/`, etc.) must be written as Obsidian wikilinks `[[filename]]` (no path, no `.md` extension) so the rendered `## Sources` section in the resulting wiki page is a clickable link. Bare paths render as plain text and break navigation. URLs and `"session capture"` stay as-is. Auto-resolution finds the file by filename anywhere in the vault — keep Reference filenames specific enough to avoid collisions.

## Reference: wiki page schema

```yaml
---
title: "Page Title"
aliases: []
tags:
- Domain/category
type: <concept|model|technique|tool|service|pattern|practice|architecture|workflow|algorithm|hardware|os>
domain: <AI|Cloud|Data|Engineering|Homelab>
status: <stub|draft|mature>
source_count: <int>
created: YYYY-MM-DD
updated: YYYY-MM-DD
related:
- '[[Page]]'
builds_on:
- '[[Page]]'
contrasts_with: []
appears_in: []
---
## How It Works
## Tensions & Open Questions
## See Also
## Sources
```
