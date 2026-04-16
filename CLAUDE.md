# knowledge-vault-ops

This repo documents and replicates the knowledge-vault system.

## Source vault

The live source vault is at `/mnt/c/Users/jonpaulboyd/Documents/knowledge-vault`
(GitHub: corticalstack/knowledge-vault). Replicators: replace this path with your own vault location.

`templates/` mirrors live files from the source vault. Before updating any template,
read the corresponding live file first, then overwrite the template to match.

| Template file | Source |
|---------------|--------|
| `templates/workflows/vault-ingest.yml` | `.github/workflows/vault-ingest.yml` |
| `templates/workflows/luminary-scan.yml` | `.github/workflows/luminary-scan.yml` |
| `templates/CLAUDE.md` | `CLAUDE.md` |
| `templates/luminaries.json` | `luminary-scan/luminaries.json` |
| `templates/wiki-page.md` | `Templates/wiki-page.md` |
| `templates/add_frontmatter.py` | `docs/scripts/add_frontmatter.py` |

## Writing register

Every doc in this repo must explain *why* decisions were made, not just *what* the
system does. Reference docs must be usable by someone replicating from scratch, not
only by the owner.

Do not reproduce the vault's wiki schema or ingestion rules inline — those are
documented in `docs/reference/wiki-schema.md` and live in `templates/CLAUDE.md`.
