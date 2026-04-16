#!/usr/bin/env python3
"""Inject stub YAML frontmatter into Obsidian .md files that lack it.

Usage:
  python add_frontmatter.py              # dry run, entire vault
  python add_frontmatter.py AI           # dry run, AI/ folder only
  python add_frontmatter.py AI --apply   # apply to AI/ folder
  python add_frontmatter.py --apply      # apply to entire vault
"""

import sys
from datetime import datetime
from pathlib import Path

VAULT = Path(__file__).parent.parent.parent  # docs/scripts/ -> vault root

DOMAIN_MAP = {
    "AI": "AI",
    "Engineering": "Engineering",
    "Cloud": "Cloud",
    "Data": "Data",
    "Homelab": "Homelab",
    "Personal": "Personal",
}

SKIP_DIRS = {".obsidian", ".git", "docs", "Assets"}


def get_domain(filepath: Path) -> str:
    parts = filepath.relative_to(VAULT).parts
    return DOMAIN_MAP.get(parts[0], "Unknown") if parts else "Unknown"


def has_frontmatter(content: str) -> bool:
    return content.lstrip().startswith("---")


def get_created_date(filepath: Path) -> str:
    return datetime.fromtimestamp(filepath.stat().st_mtime).strftime("%Y-%m-%d")


def make_frontmatter(title: str, domain: str, created: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    safe_title = title.replace('"', "'")
    return (
        f'---\n'
        f'title: "{safe_title}"\n'
        f'aliases: []\n'
        f'tags: []\n'
        f'type: concept\n'
        f'domain: {domain}\n'
        f'status: draft\n'
        f'created: {created}\n'
        f'updated: {today}\n'
        f'---\n\n'
    )


def process_file(filepath: Path, apply: bool) -> bool:
    """Return True if file needs/got frontmatter added."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"  ERROR reading {filepath}: {e}")
        return False

    if has_frontmatter(content):
        return False

    title = filepath.stem
    domain = get_domain(filepath)
    created = get_created_date(filepath)
    stub = make_frontmatter(title, domain, created)

    if apply:
        filepath.write_text(stub + content, encoding="utf-8")
    return True


def main():
    args = sys.argv[1:]
    apply = "--apply" in args
    folder_arg = next((a for a in args if not a.startswith("--")), None)

    search_path = VAULT / folder_arg if folder_arg else VAULT
    if not search_path.exists():
        print(f"ERROR: {search_path} does not exist")
        sys.exit(1)

    mode = "APPLY" if apply else "DRY RUN"
    target = folder_arg or "entire vault"
    print(f"[{mode}] Scanning: {target}\n")

    updated, skipped = 0, 0

    for md_file in sorted(search_path.rglob("*.md")):
        if any(skip in md_file.parts for skip in SKIP_DIRS):
            continue

        result = process_file(md_file, apply)
        rel = md_file.relative_to(VAULT)

        if result:
            action = "ADDED" if apply else "NEEDS"
            print(f"  {action}: {rel}")
            updated += 1
        else:
            skipped += 1

    print(f"\nResult: {updated} files {'updated' if apply else 'need frontmatter'}, {skipped} already have it")
    if not apply and updated > 0:
        print("Re-run with --apply to make changes.")


if __name__ == "__main__":
    main()
