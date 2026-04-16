# knowledge-vault-ops

A reference for how the knowledge-vault system was built, why every decision was made, and all the templates needed to replicate it from scratch.

---

## Act 1 — The problem

The vault began as roughly four thousand Obsidian notes accumulated over years of learning. Each note captured something useful in isolation — a concept, a paper summary, a configuration snippet — but the collection as a whole was nearly inert. Notes almost never linked to each other. Concepts that built on each other sat in separate files with no indication of the relationship. Searching the vault returned a list of documents; it never returned an understanding.

The deeper problem was that every query re-derived the same relationships from scratch. Ask a question about attention mechanisms and you would find the attention note, maybe a transformer note, and then spend time manually tracing connections that should have been pre-compiled years ago. The vault was a filing cabinet, not a knowledge base. Growing it made the filing cabinet heavier, not smarter.

This created a second failure: the vault was useless to agents. A language model given access to four thousand loose markdown files must re-reason about every relationship on every request. There is no shared structure it can lean on, no pre-built map of what connects to what or why. The notes existed; the knowledge did not.

---

## Act 2 — The solution

The direction came from Andrej Karpathy's writing on building a personal wiki. The key idea is that language models should do the compilation work once, not on every query. Rather than asking an LLM to derive relationships at query time, you run it over your notes in advance to extract structure, build cross-references, and synthesise connections — then store that compiled knowledge in a form both humans and agents can read directly.

The system is designed to serve two audiences simultaneously. For you in Obsidian, it produces a rich wiki where every page has structured YAML frontmatter encoding `related:`, `builds_on:`, and `contrasts_with:` wikilinks. You can navigate the vault the way you always wanted to — following genuine conceptual connections rather than hoping a search turns up the right file. For your LLMs and agents, those same pre-compiled relationships become cheap, reliable context: an agent can read a wiki page's frontmatter and immediately know what this concept relates to without having to reason about it from raw notes.

The day-zero bootstrap ran graphify over the vault — a parallel-agent tool that performs semantic extraction over markdown files, applies Leiden community detection, and produces a plain-English map of the vault's knowledge clusters. Over 1,736 nodes across 197 communities, it identified five natural domains from the existing notes: AI, Cloud, Data, Engineering, and Homelab. These were not imposed upfront — they emerged from the graph's analysis of a brownfield vault. Claude then used that graph as context to author the first generation of wiki pages. From that point, the system is self-sustaining. New material lands in an `_inbox/` folder; a GitHub Action fires, Claude reads it, decides whether to create a new page or enrich an existing one, and the wiki grows without manual housekeeping. A nightly scan monitors 43 luminaries (frontier researchers) — Karpathy, LeCun, and others — for content they authored in the last day, filters for novelty, and writes inbox files for anything that passes, so frontier ideas reach the wiki automatically.

The compiled wiki is organised around those five domains. Each domain has an index page mapping its conceptual landscape, and below that, individual pages for each concept — one page per concept, not one page per source. The same concept accumulates depth from multiple sources over time rather than generating a new file for each one.

---

## Act 3 — What this repo is

This repo is not the vault itself. It is the reference for how the vault system was built and how to reproduce it. Every architectural decision has a document explaining the reasoning, not just the outcome. All templates — GitHub Actions workflows, the CLAUDE.md that governs ingestion, the wiki page template, the frontmatter injection script — are kept here so someone starting from scratch can replicate the full pipeline without reconstructing decisions that have already been made. Reference docs are in `docs/`, organised into concepts, reference, and setup. Templates ready to copy into a new vault are in `templates/`.

---

## Architecture overview

The components form a pipeline from raw notes to compiled, agent-ready knowledge:

- **graphify** maps the vault's semantic structure into clusters and a plain-English report — [graphify](docs/reference/graphify.md)
- **frontmatter injection** organises notes into domains by writing structured YAML headers — [add_frontmatter.py](templates/add_frontmatter.py)
- **Claude** compiles wiki pages using the graph report as context, encoding relationships in structured frontmatter — [wiki schema](docs/reference/wiki-schema.md)
- **inbox mechanism** accepts new sources — drop a file in any `_inbox/` folder and the pipeline picks it up — [inbox workflow](docs/reference/inbox-workflow.md)
- **vault-ingest Action** fires on each inbox file, runs Claude to create or enrich the relevant wiki page, then deletes the source — [vault-ingest](docs/reference/github-actions.md)
- **luminary-scan Action** runs nightly to scan 43 frontier researchers for yesterday's output, filters for novelty, and writes inbox files for anything new — [luminary-scan](docs/reference/luminary-scan.md)
- **agent memory system** stores per-repo context in `projects/` folders and cross-repo learnings in `agents-shared/`, letting Claude carry knowledge between sessions — [agent memory](docs/reference/agent-memory.md)

---

To replicate this system, start with [Prerequisites](docs/setup/prerequisites.md).
