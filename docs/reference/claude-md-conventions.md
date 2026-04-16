# CLAUDE.md Conventions

## Two-Layer Architecture

| File | Scope | Contains |
|------|-------|---------|
| `~/.claude/CLAUDE.md` | Global — every repo | Session-start instructions, vault capture workflow, auto-flag heuristics |
| `knowledge-vault/CLAUDE.md` | Vault repo only | Wiki schema, ingestion rules, bidirectional link rule, YAML warning |

The two files are complementary, not redundant. The global file handles the memory and capture protocol that applies everywhere. The vault file handles the content and structural rules that apply only to the wiki.

## Layer 1: Global ~/.claude/CLAUDE.md

This file runs in every repo because it lives at the global Claude Code config path. It contains four blocks:

**Session-start instructions (run automatically, without being asked):**
1. `git pull` the vault to the latest state
2. Read `agents-shared/INDEX.md` to surface cross-repo learnings
3. Read `projects/{this-repo}/context.md` if it exists for per-repo context

**Capture workflow:** how to determine the right inbox (per-repo, agents-shared, or domain), the format for the markdown summary, the commit message convention (`capture: {title}`), and the git push sequence that triggers vault-ingest.

**Auto-flag heuristics:** four conditions that trigger a proactive capture suggestion from Claude without the user asking (see [Agent Memory](agent-memory.md) for the full list).

**Bootstrap instructions:** how to initialise a new repo in the vault — read the README and key architecture files, draft `context.md` and `patterns.md`, present for review, then commit and push.

**What a replicator must add to their own global CLAUDE.md:**

1. The vault path (replace with their own path)
2. The GitHub remote (replace with their own)
3. The session-start block (git pull, INDEX.md read, per-repo context read)
4. The capture and auto-flag sections
5. The bootstrap instructions

A starting-point template for the global `CLAUDE.md` is not provided as a separate file. Its content is tightly coupled to the vault path and GitHub remote, so it must be personalised. Use this section as the reference for what it must contain.

## Layer 2: knowledge-vault/CLAUDE.md

This file lives in the vault repository root. It is the behaviour driver for consistent wiki maintenance. Its content is mirrored in `templates/CLAUDE.md` in this repo for reference and for bootstrapping new vault instances.

It contains five blocks:

**graphify integration rules:** read `GRAPH_REPORT.md` before answering architecture or codebase questions, so Claude has community structure as context when authoring new wiki pages.

**Full wiki page schema:** all frontmatter fields, valid `type` values by domain, required body sections (`## Summary`, `## Key Concepts`, `## How It Works`, `## Connections`, `## Sources`). This is what makes vault-ingest produce schema-compliant pages without explicit per-session instruction.

**Inbox ingestion workflow:** step-by-step — read the inbox file, determine the target page and domain, apply the schema, write the page, delete the inbox file, add the source citation, check bidirectional links.

**YAML editing warning:** never overwrite the entire frontmatter block; edit only the specific field that needs changing. Overwriting silently drops fields that were populated by automation.

**Agent memory system structure and session capture workflow:** the per-repo and agents-shared directory structure, and the same capture workflow as the global file (so it is available when working in the vault repo itself).

## The Principle

Instructions live in CLAUDE.md, not in per-session prompts. A Claude session with a complete CLAUDE.md produces schema-compliant wiki pages without being told the schema. A session without it requires explicit instruction every time — and that instruction is only as reliable as the current conversation.

The more complete CLAUDE.md is, the less per-session overhead. If you find yourself repeatedly telling Claude the same thing at the start of a session, that instruction belongs in CLAUDE.md.

## See Also

- [Agent Memory System](agent-memory.md)
- [Wiki Schema](wiki-schema.md)
- [Design Principles](../concepts/design-principles.md)
