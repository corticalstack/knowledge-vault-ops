# verify-wiki.py

`verify-wiki.py` is the vault's integrity checker. It walks every `domain/category/` subdirectory and validates each wiki page against the full schema. Running it after any batch of wiki changes is the primary way to catch schema violations before they propagate.

## What It Checks

For every wiki page in every `domain/category/` subdirectory, `verify-wiki.py` validates:

**Frontmatter completeness** — all required fields must be present: `title`, `aliases`, `tags`, `type`, `domain`, `status`, `source_count`, `created`, `updated`, `related`, `builds_on`, `contrasts_with`, `appears_in`. A page missing any of these fields fails.

**Type validity** — the `type` field must be valid for the page's domain. For example, `type: concept` is valid in the `AI` domain but invalid in the `Cloud` domain (which only accepts `service`, `pattern`, `architecture`). See the type table in [wiki-schema.md](wiki-schema.md).

**Status validity** — `status` must be one of `stub`, `draft`, or `mature`.

**source_count integrity** — `source_count` must be an integer value.

**Wikilink resolution** — every wikilink in `related:`, `builds_on:`, `contrasts_with:`, and `appears_in:` must resolve to a real wiki page in the vault. Broken links (references to pages that do not exist) are reported as errors.

**Bidirectional reciprocal** — every entry in `related:` must be reciprocated: the target page must list the source page in its own `related:` field. This check is applied across all pages in a single pass, so it will catch both sides of a missing reciprocation. Note: `builds_on:` and `contrasts_with:` are one-directional and are not checked for reciprocation.

**Required body sections** — all four headings must be present, with exact text: `## How It Works`, `## Tensions & Open Questions`, `## See Also`, `## Sources`. The check is a literal string match, so capitalisation and punctuation must be exact.

## When to Run

- After every batch of wiki page writes in a manual session, before committing.
- Before committing any batch of wiki changes — treating it as a pre-commit check catches schema drift early.
- `vault-ingest` runs it automatically after every ingestion cycle; you do not need to run it manually when the Action handles the write.

Running it mid-session (before you are finished) is also useful as a progress check when creating multiple interlinked pages, since bidirectional reciprocation errors will surface as soon as you add a `related:` entry without yet updating the target page.

## Output Format

The script produces one of two outputs:

**Clean run:**
```
OK — N pages passed all checks.
```

**Errors found** — one line per violation, with the relative file path and a description:
```
AI/concepts/Large Language Model.md: missing field 'source_count'
AI/concepts/RAG.md: related '[[Embeddings]]' not reciprocated in target
Cloud/services/Azure OpenAI.md: type 'concept' invalid for domain 'Cloud'
Engineering/practices/Trunk-Based Development.md: missing section '## Tensions & Open Questions'
Data/algorithms/K-Means.md: wikilink '[[DBSCAN]]' does not resolve to any wiki page
```

Error messages always include the file path relative to the vault root, which makes it straightforward to open the affected file directly.

## How vault-ingest Uses It

`vault-ingest` runs `verify-wiki.py` automatically at the end of every ingestion. If errors are found, the Action does not silently pass — it stages a partial commit (containing whatever was successfully written) and opens a GitHub Issue titled `"Vault ingest errors: {inbox file}"`. The issue body lists the specific validation failures.

This design surfaces errors for manual review rather than allowing bad state to accumulate undetected. If you see an open issue with this title in the vault repository, it means a recent ingestion produced schema violations that need to be fixed by hand before the affected pages are considered clean.

## Location

`scripts/verify-wiki.py` in the vault root.

The script is vault-specific rather than a general-purpose tool: it hardcodes the domain names and valid category/type mappings for this particular vault layout. If you fork or replicate the vault with different domains, `verify-wiki.py` requires corresponding changes to those mappings before it will validate correctly. For this reason it lives in `scripts/` and is not included in `Templates/` — it is not a template to copy unchanged.
