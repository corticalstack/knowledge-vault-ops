# Day-0 Category Finalisation Prompt

Paste the prompt below into a Claude Code session running in your vault root, after you have compiled an initial batch of wiki pages across every domain. It observes the category subfolders that emerged naturally during compilation, proposes a final per-domain category list, and — on your approval — writes the list back into the two places that enforce it: vault `CLAUDE.md` (the `Valid types:` line) and `scripts/verify-wiki.py` (the `DOMAINS` dict).

## When to run this

- **After:** you have compiled enough wiki pages in each domain that the shape is visible (at least a handful of pages per domain, ideally ≥3 per intended category). Running earlier risks formalising a category list that is too thin to reflect the corpus.
- **Before:** you begin regular operation. `vault-ingest` reads the valid types from `CLAUDE.md` to pick a category folder for each new page; `verify-wiki.py` errors on missing category folders. Both must be in sync with reality before ingest starts producing pages.

## Prerequisites

- Vault is a git repository — this prompt edits `CLAUDE.md` and `scripts/verify-wiki.py`. Commit beforehand so you can diff the result.
- At least one batch of compiled wiki pages under `Domain/category/` folders, each with a `type:` value in its frontmatter.
- Vault `CLAUDE.md` contains a `Valid types:` line (even a placeholder one).
- `scripts/verify-wiki.py` contains a `DOMAINS` dict (the version in the reference vault is fine to start from).

## The prompt

Copy everything inside the fence into Claude Code, after `cd`-ing into your vault root.

````text
You are finalising the category taxonomy for this vault after the initial
wiki compilation pass. The category axis is orthogonal to the domain axis:
domains group pages by topic (AI, Cloud, ...), categories group them by
kind (concept, model, technique, tool, ...). This prompt does NOT touch
the domain axis or move any pages.

LEAVE UNTOUCHED (do not rename, move, or edit content):
- Any wiki page (.md under Domain/category/) — frontmatter and body unchanged
- _inbox/ folders, _INDEX.md files
- Personal/, Assets/, Templates/, References/, .obsidian/, .git/
- graphify-out/, luminary-scan/, projects/, agents-shared/, lessons-learned/

INPUTS to read before proposing:
1. Every domain folder (read from vault root — any top-level directory
   already present in the current CLAUDE.md Valid types: line, or any
   top-level directory that contains wiki pages with a type: field).
   For each: enumerate category subfolders, count pages in each, and
   collect the unique type: values used in page frontmatter.
2. Current vault CLAUDE.md — the existing `Valid types:` line (authoritative
   until this prompt rewrites it).
3. scripts/verify-wiki.py — the existing `DOMAINS` dict (authoritative
   until this prompt rewrites it).

PROCESS:

Phase 1 — Observe, propose, write proposal file.

  a. For each domain, collect:
     - Category subfolders present on disk and page count in each
     - Unique `type:` values actually used by pages in the domain
     - Inconsistencies:
         * pages whose parent folder does not match their type: value
           (e.g. page in AI/concepts/ with type: technique)
         * type: values used with no matching folder
         * category folders that exist but are empty
         * types or categories declared in current CLAUDE.md or DOMAINS
           dict that have no pages using them (candidates for pruning)
  b. Propose a final category list per domain:
     - Include only categories with ≥1 page (prune empty)
     - Each folder name (plural) must match its type: value (singular)
       by simple pluralisation: concept → concepts, service → services,
       pattern → patterns. Flag any non-standard pluralisation (e.g.
       "os" → "os", "architecture" → "architecture") explicitly.
     - Mark categories with <3 pages as `thin` — the user may want to
       merge them into a neighbour or drop them
  c. Write categories-proposal.md at the vault root:

     # Proposed category taxonomy

     ## {Domain}

     Current folders on disk: {list}
     Types in use across pages: {list}
     Inconsistencies: {list, or "none"}

     Proposed final categories:
     - `{category}/` — type: `{singular}`, N pages ({thin|healthy})
     - `{category}/` — type: `{singular}`, N pages ({thin|healthy})

     (repeat per domain)

     ## Files that Phase 2 will edit
     - CLAUDE.md — rewrite the `Valid types:` line
     - scripts/verify-wiki.py — rewrite the DOMAINS dict

  d. Stop after writing categories-proposal.md. Report:
     - per-domain proposed category count
     - total inconsistencies flagged
     - any thin categories
     Ask: "Review categories-proposal.md. Reply 'apply' to write the
     updates to CLAUDE.md and verify-wiki.py, or edit the proposal
     (drop a thin category, merge two, rename, reassign) before
     replying. Page-level inconsistencies are out of scope — resolve
     those separately by renaming folders or editing type: values."

Phase 2 — Apply (only after user replies 'apply'):

  a. Re-read categories-proposal.md for the authoritative list.
  b. Rewrite the `Valid types:` line in vault CLAUDE.md:
     - Format: `Valid types: {Domain} → {t1}/{t2}/... · {Domain} → ...`
     - Use the singular type values from the proposal.
  c. Rewrite the DOMAINS dict in scripts/verify-wiki.py:
     - Preserve the dict shape: each key is a domain, value is
       {'types': {set of singulars}, 'categories': [list of plurals]}
     - Keep existing Python style (indentation, comma trailing, etc.)
  d. Run `python3 scripts/verify-wiki.py` and capture the output.
     Report errors — the common failure is a page whose type: now falls
     outside the tightened set. The user resolves those before committing.
  e. Do NOT move or rename any wiki pages. Do NOT edit page frontmatter.
     Those are manual decisions deferred to the user.
  f. Stage everything: `git add -A`
  g. Stop. Do not commit. The user will review `git status` (expect two
     changed files) and commit with a message like "bootstrap: finalise
     category taxonomy".
````

## Notes on the design

- **Categories are discovered, not designed.** The reorganise prompt discovered domain names from graphify's clustering. This prompt does the same for categories, but at a different moment — after compilation, because compilation is where "what kinds of pages does this corpus produce" becomes visible. Running this pre-compilation would force Claude to guess from raw inbox content.
- **Why two load-bearing files.** `vault-ingest` reads `CLAUDE.md` at session start to know what category folder to place a new page in. `verify-wiki.py` walks `Domain/category/` paths explicitly. Skip either and ingest will place pages in nonexistent folders, or verify will miss whole categories.
- **No page renames.** Folder / type inconsistencies are flagged but not auto-fixed. A page in `AI/concepts/` with `type: technique` could be (a) correctly categorised, wrong type; (b) correct type, wrong folder. The prompt cannot tell, and guessing breaks backlinks. Surface, defer.
- **Thin-category warning.** A category with 1–2 pages often indicates either (a) a category that should be absorbed into a neighbour, or (b) a genuinely sparse but valid slot. The prompt flags without deciding.
- **Orthogonal to the reorganise prompt.** That prompt's job is `flat → domain-bucketed` (topic axis). This prompt's job is `emerged-categories → formalised-categories` (kind axis). Keeping them separate avoids conflating two different judgments.

---

**Runs once, near the end of Day-0.** After this, category additions are manual: add a `Domain/newcategory/` folder, extend the `Valid types:` line in `CLAUDE.md`, extend the `DOMAINS` dict in `verify-wiki.py`. Re-run this prompt only if the taxonomy drifts significantly — not for one-off additions.
