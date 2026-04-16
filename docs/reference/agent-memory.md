# Agent Memory System

## Purpose

The vault stores agent knowledge that would otherwise be lost between sessions. When a Claude session ends, everything discussed — architectural decisions, tricky tradeoffs, bugs that took an hour to track down — disappears from context. The agent memory system captures that knowledge to disk and replays it at the start of the next session.

This crosses repo boundaries. Learnings from one repo are available in all other repos at the next session start. An agent working in a new repository starts with the accumulated understanding built across all previous sessions in all previous repositories.

## Directory Structure

```
projects/{repo-name}/
  context.md         — architectural decisions and tradeoffs for this repo
  patterns.md        — conventions and preferred patterns
  _inbox/            — session captures queue

agents-shared/
  INDEX.md           — read at every session start (all repos)
  patterns.md        — cross-repo conventions
  mistakes.md        — bugs and gotchas to avoid
  _inbox/

lessons-learned/{domain}/
  {lesson-title}.md  — one file per lesson, domain-organised
```

`lessons-learned/` is created and populated automatically by the vault-ingest GitHub Action when captures include a lesson that warrants its own file.

## How It Works in Practice

**Session capture.** Say "capture this to the vault" — Claude determines the right destination (per-repo inbox, agents-shared inbox, or a domain inbox), writes a well-formed markdown summary, commits, and pushes. The vault-ingest GitHub Action fires on the push and updates the right file — creating it if it does not yet exist, enriching it if it does.

**Session start.** Claude reads `agents-shared/INDEX.md` — this surfaces cross-repo learnings without requiring Claude to read every file in the vault. If `projects/{this-repo}/context.md` exists, it is also read. Both reads happen automatically, without being asked, at the start of every session in every repository. This is specified in the global `~/.claude/CLAUDE.md`.

## What Gets Captured

The global `CLAUDE.md` defines four conditions under which Claude proactively suggests capturing:

1. A novel technology stack not yet in the wiki has been discussed in depth.
2. A non-obvious tradeoff took significant reasoning to resolve.
3. A bug's root cause wasn't documented in any source.
4. An architectural decision has a "why" not visible in the code.

These are heuristics for the agent, not a rigid checklist. When one of these conditions is met, Claude surfaces a capture suggestion — the user confirms or declines. The user can also trigger a capture explicitly at any time by saying "capture this to the vault."

## agents-shared/INDEX.md

This file is the single most load-bearing file in the agent memory system. It is loaded at every session start regardless of which repo is active. It must be kept current as `patterns.md` and `mistakes.md` grow — a stale INDEX means agents miss important learnings.

It contains two sections:

- **A table of files** with a one-line purpose description for each.
- **A Key Entries section** summarising the most important patterns and mistakes so Claude can act on `INDEX.md` alone without reading the full files.

The Key Entries section is the payoff: it means that the most critical cross-repo knowledge (known bugs, important conventions, patterns with non-obvious reasons) is surfaced in the first file Claude reads, not buried in a file that requires a second read to retrieve. When a new entry is significant enough to affect future sessions immediately, it belongs in Key Entries, not just in the body of `patterns.md` or `mistakes.md`.

## See Also

- [Vault Structure](vault-structure.md)
- [Inbox Workflow](inbox-workflow.md)
- [CLAUDE.md Conventions](claude-md-conventions.md)
- [Design Principles](../concepts/design-principles.md)
