# graphify

## What It Is

Package: `graphifyy` (double y) — `pip install graphifyy`. Runs parallel Claude agents for semantic extraction over a directory of markdown files, applies Leiden community detection, and produces three outputs.

Source repository: [https://github.com/safishamsi/graphify](https://github.com/safishamsi/graphify)

## Outputs

| Output | Purpose |
|--------|---------|
| `graph.json` | Machine-readable graph (nodes, edges, communities) |
| `graph.html` | Interactive visual (zoom, pan, click) |
| `GRAPH_REPORT.md` | Plain-English report: god nodes, surprising connections, hyperedges — the only output an LLM can read directly |

All three are written to `graphify-out/` in the vault root.

## Day-0 Bootstrap

The following sequence was used to establish the vault's domain structure from a flat collection of ~4,000 notes.

1. Run graphify over the raw vault:
   ```bash
   graphify . --output graphify-out/
   ```
2. Read `graphify-out/GRAPH_REPORT.md`. Look for: which concepts have the most connections (god nodes), which clusters are cohesive, which files are semantic outliers.
3. Identify natural clusters from the report. The report surfaces which concepts naturally group together — use those groupings to decide domain names.
4. Define domain folders manually. Graphify identified the domains; the folder structure was created manually. graphify did not automatically create folders.
5. Relocate misplaced notes into the new domain/category structure.
6. Run `add_frontmatter.py` to generate initial frontmatter for all relocated pages.

**Bootstrap stats from the original run:** 21 parallel extraction agents processed 446 files, producing 1,736 nodes and 1,792 edges across 197 Leiden communities. Five domains were identified: AI, Cloud, Data, Engineering, Homelab.

**God nodes from the original run** (highest edge counts): ML Terminology (27 edges), Azure AZ-305 (17), Azure DevOps Pipelines (14). These are the most semantically central concepts in the vault — any new page touching these topics should reference them.

## Ongoing Incremental Use

```bash
# Incremental update, entire vault
graphify . --update

# One domain only
graphify AI/ --update
```

Run after every batch of 5 or more new wiki pages. This keeps the community structure current as the corpus grows.

Do not run for frontmatter fixes or typo edits — no semantic content changed and the graph output would be identical.

## Reading GRAPH_REPORT.md

Three uses before a wiki expansion session:

1. **Identify thin communities.** Clusters with few pages signal gaps — areas the vault knows about but has not yet developed. These are good candidates for the next round of page creation.
2. **Find god nodes.** The most-connected concepts are structural anchors. New pages on related topics should reference these nodes to keep the graph well-connected.
3. **Spot surprising cross-domain connections.** The report highlights pairs or clusters that span domains unexpectedly. These are candidates for `related:` links in frontmatter — wiring concepts that are semantically close even when they live in different domain folders.

## Integration with CLAUDE.md

The vault `CLAUDE.md` instructs Claude to read `GRAPH_REPORT.md` before answering architecture or codebase questions. This means Claude always has the graph's community structure as context when authoring new wiki pages — it knows which concepts cluster together without being explicitly told. The instruction is in the vault `CLAUDE.md`, not in per-session prompts, so it fires automatically at every session start in the vault repo.

## See Also

- [Vault Structure](vault-structure.md)
- [Wiki Schema](wiki-schema.md)
- [Design Principles](../concepts/design-principles.md)
