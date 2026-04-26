# graphify

> Only add this block if you use the graphify skill. Delete this section otherwise.

- **graphify** (`~/.claude/skills/graphify/SKILL.md`) - any input to knowledge graph. Trigger: `/graphify`
When the user types `/graphify`, invoke the Skill tool with `skill: "graphify"` before doing anything else.

# Knowledge Vault

Vault is at `/path/to/your-vault` (git-backed, synced to GitHub at `your-github-username/your-vault-repo`).

## Session start (every repo) — RUN THESE AUTOMATICALLY, WITHOUT BEING ASKED

At the very start of every session, before responding to any user message, run all of these steps:

1. `git -C /path/to/your-vault pull --ff-only --quiet`
2. Read `/path/to/your-vault/agents-shared/INDEX.md`
3. If `/path/to/your-vault/projects/{this-repo-name}/context.md` exists, read it
4. For domain-specific work: `grep -rl "{concept}" /path/to/your-vault --include="*.md" | head -5` then read matches

Do not wait for the user to ask. Do not announce that you are doing it. Just do it silently as part of session initialisation.

## Capture during sessions

When asked to "capture this to the vault" or when auto-flagging a novel concept:
1. New concept not in wiki → `/path/to/your-vault/{AI|Cloud|Data|Engineering|Homelab}/_inbox/`
2. Repo-specific architectural decision or tradeoff → `/path/to/your-vault/projects/{repo-name}/_inbox/`
3. Cross-repo pattern or gotcha → `/path/to/your-vault/agents-shared/_inbox/`

Write a well-formed markdown summary to the inbox, then:
`git -C /path/to/your-vault add -A && git commit -m "capture: {title}" && git push`
The vault-ingest GitHub Action fires automatically and creates/updates wiki pages.

## Auto-flag heuristics

Proactively suggest capturing when:
- A novel technology stack not yet in the wiki has been discussed in depth
- A non-obvious tradeoff took significant reasoning to resolve
- A bug's root cause wasn't documented in any source
- An architectural decision has a "why" not visible in the code

## Bootstrap a new repo

When asked "Bootstrap this repo in the vault":
1. Read README, CLAUDE.md, `git log --oneline -50`, key architecture files
2. Draft `/path/to/your-vault/projects/{repo-name}/context.md` (architecture decisions, tradeoffs)
3. Draft `/path/to/your-vault/projects/{repo-name}/patterns.md` (conventions, preferred patterns)
4. Present both for review, then commit and push to vault
