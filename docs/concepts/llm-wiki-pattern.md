# The LLM Wiki Pattern

## The Core Insight

In a traditional note-taking workflow, knowledge accumulates as raw fragments: meeting notes, article excerpts, quick captures, half-finished summaries. When you later ask an LLM a question over that corpus, the model searches, retrieves those fragments, and re-derives relationships at query time — every single time. Cross-references are never stored. Contradictions are never surfaced and resolved. Synthesis is always a one-off artefact, discarded at the end of the context window.

The wiki pattern — inspired by Andrej Karpathy's framing of LLMs as knowledge compilers — inverts this. Instead of deferring synthesis to query time, an LLM incrementally compiles raw sources into structured, interlinked pages. Relationships between concepts are computed once and written down. Contrasts, prerequisites, and summaries are baked into the page itself, not reconstructed on demand. A question answered by reading a well-formed wiki page is answered faster and with more fidelity than the same question answered by re-examining the pile of sources it was compiled from.

## Why It Matters for Agents

Agent context windows are finite. Every token spent re-reading raw source material is a token not available for reasoning about the actual task. A dense wiki page — one that names its prerequisites, lists its related concepts as wikilinks, and contains synthesised prose rather than copied fragments — delivers far more signal per token than a folder of notes on the same topic. The wiki is not just a convenient format for human browsing; it is optimised specifically for agentic consumption. When an agent reads `agents-shared/INDEX.md` at session start, it is receiving pre-compiled, cross-referenced context that would otherwise require many more tokens and several retrieval passes to reconstruct from raw sources.

## How graphify Enables It

Running graphify over a corpus of raw notes does something that neither the author nor Claude can easily do alone: it surfaces the natural knowledge structure of the domain. Leiden community detection groups semantically related concepts into clusters, identifying which ideas belong together, which nodes are central hubs connecting many concepts, and which communities are thin and underrepresented. The output — GRAPH_REPORT.md — is a plain-English report Claude reads directly before authoring wiki pages. With this map, Claude knows which concepts should share a page, which pages should link to each other in their `related:` frontmatter, and which prerequisites to explain first. The graph is the scaffolding; Claude is the author. graphify does not write the wiki — it makes the writing structurally sound.

## The Compounding Effect

Every new source file dropped into the vault inbox enriches the wiki rather than just adding to a pile. When an existing page is updated, its `source_count` frontmatter field increments, and its status advances through stub, draft, and mature as evidence accumulates. New wikilinks wire it more tightly into the graph. Agents starting new sessions in entirely different repositories inherit this accumulated knowledge through the `agents-shared/` layer, which surfaces cross-repo learnings regardless of which project is active. The benefit is not linear — each addition makes every subsequent retrieval richer, and knowledge that compounds across sessions also compounds across repos.

## See Also

- [Design Principles](design-principles.md)
- [graphify](../reference/graphify.md)
- [Agent Memory](../reference/agent-memory.md)
