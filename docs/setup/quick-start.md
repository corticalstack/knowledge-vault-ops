# Quick Start

## Day-0 Sequence

These steps take you from an empty vault to a fully operational system. Work through them in order — each step depends on the previous one.

**Before you begin:** Clone this repo so `templates/` is available locally:
```bash
git clone https://github.com/corticalstack/knowledge-vault-ops
```

Commands in these steps run from two different directories:
- Steps 7 and 9 run **from your vault root** (where your Obsidian notes live)
- All other steps run from wherever is convenient

1. **Install graphify**:
   ```bash
   pip install graphifyy
   ```

2. **Run graphify over your vault**:
   ```bash
   graphify /path/to/vault
   ```
   This produces a `graphify-out/` directory containing `GRAPH_REPORT.md`, `graph.html`, and `graph.json`.

3. **Read `GRAPH_REPORT.md`**: identify natural clusters. These become your domain folders. Look for:
   - **God nodes** — the most-connected concepts, which indicate central themes
   - **Cohesive communities** — tight clusters that naturally belong together in a domain
   - **Thin communities** — sparse clusters that may not warrant their own domain

4. **Create domain folder structure manually**: create top-level folders for each domain (e.g. `AI/`, `Cloud/`, `Data/`). Inside each domain, add category subdirectories (`concepts/`, `tools/`, etc.) and an `_inbox/` folder. Also create an `_INDEX.md` at the domain level and at the vault root level.

5. **Create `.base` files per domain** (optional but recommended for Obsidian navigation): `wiki-recent.base`, `wiki-stubs.base`, `wiki-mature.base`, `wiki-review.base`. Reference copies are in the source vault on GitHub at [corticalstack/knowledge-vault/tree/main/AI](https://github.com/corticalstack/knowledge-vault/tree/main/AI) — these files define the Obsidian Bases views that make the wiki browsable by recency, stub status, and maturity.

6. **Relocate misplaced notes**: move any notes sitting in the wrong domain folder to their correct location. This is manual curation — graphify's cluster report will highlight most of the obvious cases.

7. **Run `add_frontmatter.py`** — copy it to your vault first, then run from the vault root:
   ```bash
   # From the knowledge-vault-ops clone:
   cp templates/add_frontmatter.py /path/to/your-vault/docs/scripts/add_frontmatter.py

   # Then, from your vault root:
   python docs/scripts/add_frontmatter.py              # dry run — shows what would change
   python docs/scripts/add_frontmatter.py --apply      # apply to entire vault
   ```
   This stamps every note with the standard frontmatter schema (domain, category, maturity, etc.) that vault-ingest and the wiki schema depend on.

8. **Begin wiki compilation**: use Claude with `GRAPH_REPORT.md` as context to build wiki pages for each domain. Use `templates/wiki-page.md` as the starting template for each page. Work domain by domain rather than trying to do the whole vault in one pass.

9. **Run `verify-wiki.py` after each batch** (run from your vault root — `scripts/verify-wiki.py` is vault-specific and lives in the vault, not in this repo):
   ```bash
   python3 scripts/verify-wiki.py
   ```
   Fix all reported errors before committing. Running this after each batch catches schema drift early rather than accumulating a large backlog of invalid pages.

10. **Copy `CLAUDE.md` to vault root**: copy `templates/CLAUDE.md` into your vault repository root. This file instructs Claude to behave as a consistent wiki maintainer — it governs how vault-ingest writes and enriches pages.

11. **Add global `CLAUDE.md`**: update your `~/.claude/CLAUDE.md` with the session-start, capture, and auto-flag instructions. These make Claude vault-aware across all projects, not just when working directly in the vault. See [CLAUDE.md Conventions](../reference/claude-md-conventions.md) for the exact blocks to add.

12. **Copy workflow YAMLs**: copy the contents of `templates/workflows/` to `.github/workflows/` in your vault repository. These are the two Action definitions (`vault-ingest.yml` and `luminary-scan.yml`).

13. **Add GitHub secrets**: add `CLAUDE_CODE_OAUTH_TOKEN` and `VAULT_PAT` to your vault repository. See [Prerequisites](prerequisites.md) for where to find each token and how to add them.

13b. **Initialise luminary-scan files**: copy `templates/luminaries.json` to `luminary-scan/luminaries.json` in your vault, edit to match your focus areas (see [Configuration](configuration.md#luminaries-roster)), then create an empty `luminary-scan/seen-urls.json`:
   ```bash
   echo '[]' > luminary-scan/seen-urls.json
   ```
   Commit and push both files. The luminary-scan Action will fail if either is missing.

14. **Test vault-ingest**: drop a `.md` file into any `_inbox/` folder, commit and push (Obsidian Git does this automatically if auto-push is enabled), then watch the Action run in GitHub → Actions tab. The test is successful when the inbox file has been deleted and a new wiki page has appeared in a commit starting with `ingest:`.

## Verifying It Works

After step 14, check the two Actions independently:

**vault-ingest**: the inbox file you dropped should be deleted, a wiki page should be created or updated, and the commit message should start with `ingest:`. If the Action ran but made no commit, check the Action log — it will show whether Claude's output was valid or was rejected by the schema check.

**luminary-scan**: trigger manually via the Actions tab → select "Luminary Scan" → "Run workflow" → Run. After it completes, commits starting with `scan({slug}):` should appear in the repository. If any content was captured, vault-ingest will have been triggered automatically by each per-luminary push — check the Actions tab for vault-ingest runs that followed the scan immediately.
