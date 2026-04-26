# Day-0 Vault Reorganisation Prompt

Paste the prompt below into a Claude Code session running in your vault root, after you have run `graphify`. It runs in three phases: (1) proposes a small set of top-level domain names by rolling up graphify's fine-grained communities, (2) plans where every loose note should move, (3) applies the moves with `git mv`. Each phase stops for your review.

## When to run this

- **After:** `graphify-out/GRAPH_REPORT.md` and `graphify-out/graph.json` exist at the vault root. You do **not** need to have picked domain names — the prompt proposes them.
- **Before:** running `add_frontmatter.py`. The script derives `domain:` from the top-level folder, so notes must already sit under their domain before it runs.

## Prerequisites

- Vault is a git repository. The prompt moves many files — commit beforehand so you can diff the result.
- `graphify-out/GRAPH_REPORT.md` and `graphify-out/graph.json` exist at the vault root.
- Loose notes at the vault root and / or under a legacy flat layout (no per-domain folders yet).

## The prompt

Copy everything inside the fence into Claude Code, after `cd`-ing into your vault root.

````text
You are reorganising this Obsidian vault from a flat layout into a small number
of top-level domain folders. Work entirely inside the current directory.

LEAVE UNTOUCHED (do not move, rename, or classify):
- Personal/, Assets/, Templates/, References/, .obsidian/, .git/
- _INDEX.md, VAULT_GUIDE.md, CLAUDE.md at the vault root
- graphify-out/, luminary-scan/, scripts/, docs/
- projects/, agents-shared/, lessons-learned/

INPUTS to read before starting:
1. graphify-out/GRAPH_REPORT.md — fine-grained topical communities (typically
   50–100 of them), god nodes, cross-domain bridges; community labels also
   carry kind signals (Models, Techniques, Tools…) used in Phase 1c
2. graphify-out/graph.json — node → community mapping; node `id` fields carry
   type prefixes (concept_, tool_, technique_, model_…) used in Phase 1c to
   derive the per-domain category type starter list

PROCESS:

Phase 1 — Propose top-level domain names and category types. No writes to the vault tree.

  a. Read GRAPH_REPORT.md. Note that graphify's communities are fine-grained
     topical clusters ("LLM Architecture and Fine-Tuning", "Azure Identity and
     Networking", etc.). These are NOT the top-level domain names — they are
     the raw clusters that need rolling up.
  b. Roll the fine-grained communities into a small set of top-level domains
     (aim for 4–7). Each domain should:
       - Be a short noun or noun phrase, one word where possible (e.g. "AI",
         "Cloud", "Homelab")
       - Cover multiple graphify communities that share a coherent theme
       - Be stable — a label you would still recognise a year from now even
         as sub-topics shift
     Skip communities that are corpus artefacts rather than real topics (e.g.
     "Inbox", "Review Queue", "Vault Infrastructure"). They will be absorbed
     by the domains their notes belong to once moved.
  c. Derive a per-domain category type starter list from graph.json.
     Category types describe the *kind* of a note (concept, model, technique,
     tool…), orthogonal to the domain (topic). graphify encodes this in node IDs.
     i.   Read graph.json. For every node, inspect its `id` field for a
          recognisable type prefix (case-insensitive, strip trailing `_`):
            concept_, model_, technique_, tool_, practice_, service_, pattern_,
            algorithm_, workflow_, architecture_, hardware_, os_
     ii.  Also scan community labels in GRAPH_REPORT.md for kind signals:
          community names containing words like Models, Techniques, Tools,
          Services, Patterns, Concepts, Practices are secondary signals (use
          when node-ID prefix counts are sparse).
     iii. Map each typed node to its domain via the community → domain
          assignments from step b. Per domain, tally prefix occurrences.
     iv.  Propose a normalised type vocabulary per domain:
          - Use the singular English form: concept, model, technique, tool, etc.
          - Include a type if ≥3 nodes in that domain carry its prefix, OR if a
            community label signals it and the domain clearly contains that kind
          - Flag types with <3 nodes as `thin` — candidates for merging into a
            neighbouring type or dropping if the domain has no natural use
          - Types that are universal (e.g. concept, tool) may repeat across domains
  d. Write domain-proposal.md at the vault root:

     # Proposed top-level domains

     ## {Domain name}
     Rubric: one-line description of what belongs in this domain
     Source communities:
     - Community N — "{community label}" (NN nodes)
     - Community M — "{community label}" (NN nodes)

     ## {Domain name}
     ...

     ## Skipped communities
     - Community K — "{label}" — reason (e.g. "corpus artefact, absorbed by
       destination domain of member notes")

     ## Proposed category types per domain

     ### {Domain}
     Observed prefixes: {prefix: count, ...}
     Community label signals: {list or "none"}
     Proposed types (singular): {type1, type2, ...}
     Thin (<3 nodes): {list or "none"}

     ### {Domain}
     ...

     ## Valid types line (for vault CLAUDE.md)
     Valid types: {Domain} → {t1}/{t2}/... · {Domain} → ...

  e. Stop after writing domain-proposal.md. Report:
     - proposed domain count, names, and one-line rubrics
     - per-domain proposed category types (count and any thin ones)
     - any graphify communities assigned to more than one domain (bridges —
       flag them but keep a primary assignment)
     - any communities you skipped and why
     Ask: "Review domain-proposal.md. Reply 'proceed' to plan the file moves
     and write the Valid types line into vault CLAUDE.md, or edit the proposal
     (rename/merge/split a domain, drop a thin category type, reassign a
     community) before replying."

Phase 2 — Plan file moves. No writes to the vault tree.

  a. Re-read domain-proposal.md in case the user edited it. This is now the
     authoritative domain list.
  b. Enumerate every .md file at the vault root and in any legacy flat
     subfolder that is not in the untouched list above.
  c. For each file, assign exactly one domain using:
       1st signal: graphify community membership from graph.json, mapped to a
                   domain via domain-proposal.md
       2nd signal: read the file's title and first ~500 chars of body, match
                   against the domain rubric
       Tiebreak:   prefer the domain where the note would have the most
                   related existing content; borderline notes go to the
                   domain whose rubric words appear most frequently in the
                   note body
  d. Flag ambiguous notes — any where graphify's signal disagrees with the
     content signal, or where content signal is weak (generic / meta notes).
  e. Write reorganise-plan.md at the vault root:

     | Source path | Proposed domain | Confidence | Signal source | Flag |

     Confidence: high | medium | low
     Signal source: graphify | content | both-agree | both-disagree
     Flag: blank, or "ambiguous — review"

  f. Stop after writing reorganise-plan.md. Report:
     - total files planned to move, grouped by domain
     - count of ambiguous flags
     - any untouched files you deliberately skipped and why
     Ask: "Review reorganise-plan.md. Reply 'apply' to proceed, or edit the
     plan file to change any row's Proposed domain before replying."

Phase 3 — Apply (only after user replies 'apply'):

  a. Re-read reorganise-plan.md in case the user edited it.
  b. Re-read domain-proposal.md. Extract the `Valid types:` line from the
     `## Valid types line` section.
  c. Write that line into vault CLAUDE.md. If a `Valid types:` line already
     exists, replace it in place. If CLAUDE.md does not yet exist at the vault
     root, create it containing only that line — the full session-start rules
     are added separately (step 9 of the quickstart). Never insert the line
     twice.
  d. For each domain that will receive files, ensure the folder exists at the
     vault root. Inside each, ensure an _inbox/ subfolder exists.
  e. Move each planned file with `git mv` so history is preserved. If git mv
     fails (e.g. file not tracked), fall back to `mv` and `git add` the result.
  f. Do NOT create category subfolders (concepts/, models/, etc.) at this
     stage — those come during wiki compilation, not reorganisation.
  g. Do NOT generate or modify frontmatter. add_frontmatter.py handles that
     after reorganisation completes.
  h. After moves, write reorganise-summary.md at the vault root:
     - per-domain file counts after the move
     - any files that failed to move and why
  i. Stage everything: `git add -A`
  j. Stop. Do not commit. The user will review `git status` (expect domain
     folders, reorganise-summary.md, domain-proposal.md, and the Valid types
     update in CLAUDE.md) and commit with a message like
     "reorganise: flat vault → N domains, seed category types".
````

## Notes on the design

- **Three phases with two pauses** — domain names and per-file assignments are two separate decisions. Letting you review and edit the domain rollup before the per-file plan is generated means a rename or merge doesn't invalidate 4,000 classification rows. The plan pause is a second, finer-grained review before `git mv` touches anything.
- **Claude proposes the domain names, not the human** — graphify produces 50–100 fine-grained topical communities, not 5 tidy domain labels. Rolling them up into a small stable set is a classification judgment Claude can make from the report and then hand to you for approval. You are a reviewer of the proposal, not the originator.
- **`git mv`, not `mv`** — Obsidian's backlinks are pathname-based. Preserving git history across the move means `git log --follow` still works on every note.
- **Category types from graphify, not guesswork** — graphify node IDs encode the kind of each note in their prefix (`concept_`, `tool_`, `technique_`, `model_`, etc.). Deriving the `Valid types:` line from those prefixes before compilation begins is more faithful than inheriting a template default. The categories prompt (Day-0 step 7) still runs after compilation to prune or rename what emerged — but now it ratifies a graphify-derived seed rather than an arbitrary list.
- **No category subfolders yet** — `concepts/`, `models/`, etc. are filled during wiki compilation (later step). The `Valid types:` line seeds which kinds are legal; the folders emerge as pages are compiled.
- **No frontmatter writes** — `add_frontmatter.py` runs next and uses the folder path as the authoritative domain signal. Letting the reorganisation prompt also write frontmatter creates two sources of truth.
- **Untouched list is a hard boundary** — `projects/`, `agents-shared/`, `lessons-learned/` are infrastructure, not wiki pages. `Personal/` and `Assets/` are explicitly out of scope. The prompt lists them so Claude doesn't accidentally reclassify them as domain notes.
