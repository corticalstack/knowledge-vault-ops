# Design Principles

Five principles are implicit in every structural decision this system makes. Understanding them resolves ambiguity when the system needs to be extended or adapted — they explain not just what the system does but why it is built the way it is.

## 1. Inbox as Transient Interface

Raw source files are deleted after ingestion. What persists is not the source but the citation: a reference in the `## Sources` section of the wiki page the source enriched. Keeping raw source copies alongside compiled wiki pages creates duplicate search results in Obsidian and blurs the distinction between source material and compiled knowledge. An inbox that grows without being emptied is not an inbox — it is a second, worse knowledge base competing with the first. The inbox is a queue, not an archive. Its job is to accept new material and disappear.

## 2. Bidirectional Links as Contracts

If Page A lists `[[Page B]]` in its `related:` frontmatter, Page B must list `[[Page A]]` back. This is enforced by `verify-wiki.py`. The rationale is simple: following any link should always surface the full relationship. A reader who navigates from A to B should find B already knows about A — no dead ends, no asymmetric awareness. An unreciprocated link is not a style choice or a minor omission; it is a structural bug. It means the graph is incomplete, that a relationship exists in one direction only, and that any agent or human traversing the graph will receive a distorted picture of how concepts relate. `verify-wiki.py` exists specifically because this class of error is easy to introduce and invisible without automated checking.

## 3. Agent Memory Crossing Repo Boundaries

The vault's `agents-shared/` directory surfaces cross-repo learnings at the start of every Claude Code session, regardless of which repository is active. Per-repo context lives in `projects/{repo-name}/context.md` and persists architectural decisions, tradeoffs, and non-obvious choices that would otherwise be lost when a session ends. Together, these two layers mean that knowledge does not reset at repo boundaries. An agent working in a new repository starts with the accumulated understanding built across all previous sessions in all previous repositories. This is the mechanism by which the system's value compounds over time rather than resetting with each context window.

## 4. CLAUDE.md as Behaviour Driver

The more complete a CLAUDE.md file is, the less per-session prompting is needed to produce consistent output. Relying on conversational instruction to establish ingestion rules, schema requirements, or integrity constraints means those constraints are only as reliable as the current conversation — they vanish when the session ends. The vault's CLAUDE.md contains the full wiki schema, the ingestion workflow, and the integrity constraints in one place. This is what makes every vault-ingest run produce schema-compliant pages without explicit instruction: Claude reads the behaviour spec at session start and follows it. The global `~/.claude/CLAUDE.md` extends this pattern to every repository, ensuring the session-start protocol (pull the vault, read `agents-shared/INDEX.md`) runs automatically in every context without requiring a separate reminder.

## 5. Graphify as Map, Not Author

graphify identifies domain structure: which concepts cluster together, which nodes are highly connected hubs, which communities are sparse and underdeveloped. It does not generate wiki content. The distinction matters in practice as well as in principle. Claude is the author; the graph is the map Claude reads before writing. Deciding when to re-run graphify follows from this: re-run it after changes that alter the semantic structure of the corpus — new domains added, significant new sources ingested, major reorganisation of page relationships. Skip it for changes that do not alter semantic content: frontmatter corrections, typo fixes, formatting adjustments. Treating graphify as an author rather than a map leads to over-running it (wasting time on structural analysis that yields no new information) or under-running it (authoring wiki pages without understanding how concepts relate).

## See Also

- [LLM Wiki Pattern](llm-wiki-pattern.md)
