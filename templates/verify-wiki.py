#!/usr/bin/env python3
"""Verify wiki integrity: frontmatter completeness, wikilinks, bidirectional reciprocals."""
import re
import sys
import yaml
from pathlib import Path

REQUIRED_FIELDS = [
    'title', 'tags', 'type', 'domain', 'status', 'source_count',
    'created', 'updated', 'related', 'builds_on', 'contrasts_with', 'appears_in'
]
VALID_STATUSES = {'stub', 'draft', 'mature'}

# Domain → valid types and category subfolders
DOMAINS = {
    'AI':          {'types': {'concept', 'model', 'technique', 'tool'},
                   'categories': ['concepts', 'models', 'techniques', 'tools']},
    'Cloud':       {'types': {'service', 'pattern', 'architecture'},
                   'categories': ['services', 'patterns', 'architecture']},
    'Data':        {'types': {'concept', 'algorithm', 'workflow', 'tool'},
                   'categories': ['concepts', 'algorithms', 'workflows', 'tools']},
    'Engineering': {'types': {'practice', 'tool', 'pattern'},
                   'categories': ['practices', 'tools', 'patterns']},
    'Homelab':     {'types': {'hardware', 'os', 'service'},
                   'categories': ['hardware', 'os', 'services']},
}


def parse_frontmatter(path: Path):
    """Return (frontmatter_dict, body_str) or (None, full_content) if no frontmatter."""
    content = path.read_text(encoding='utf-8')
    if not content.startswith('---\n'):
        return None, content
    try:
        end = content.index('\n---\n', 4)
    except ValueError:
        return None, content
    try:
        fm = yaml.safe_load(content[4:end])
    except yaml.YAMLError:
        return None, content
    return fm, content[end + 5:]


def strip_wikilink(link: str) -> str:
    """'[[RAG]]' → 'RAG'"""
    return re.sub(r'^\[\[|\]\]$', '', link.strip())


def main() -> int:
    errors = []
    pages = {}          # path → (frontmatter, body)
    title_to_path = {}  # title string → path

    # Collect all non-index wiki pages across all domains
    for domain, cfg in DOMAINS.items():
        for cat in cfg['categories']:
            cat_dir = Path(domain) / cat
            if not cat_dir.exists():
                errors.append(f"MISSING CATEGORY DIR: {cat_dir}")
                continue
            for md in sorted(cat_dir.glob('*.md')):
                if md.name.startswith('_'):
                    continue
                fm, body = parse_frontmatter(md)
                if fm is None:
                    errors.append(f"MISSING FRONTMATTER: {md}")
                    continue
                pages[md] = (fm, body)
                title = fm.get('title')
                if title:
                    title_to_path[title] = md

    # Validate each page
    for path, (fm, body) in pages.items():
        # Determine domain from path
        page_domain = path.parts[0] if path.parts else 'Unknown'
        valid_types = DOMAINS.get(page_domain, {}).get('types', set())

        # Required fields present
        for field in REQUIRED_FIELDS:
            if field not in fm:
                errors.append(f"MISSING FIELD '{field}': {path}")

        # Type and status values
        if fm.get('type') not in valid_types:
            errors.append(f"INVALID TYPE '{fm.get('type')}' for domain {page_domain}: {path}")
        if fm.get('status') not in VALID_STATUSES:
            errors.append(f"INVALID STATUS '{fm.get('status')}': {path}")

        # source_count is an integer
        sc = fm.get('source_count')
        if not isinstance(sc, int):
            errors.append(f"INVALID source_count '{sc}' (must be int): {path}")

        # Wikilinks in relationship fields resolve to real pages
        for field in ['related', 'builds_on', 'contrasts_with', 'appears_in']:
            for link in (fm.get(field) or []):
                target = strip_wikilink(link)
                if target not in title_to_path:
                    errors.append(f"BROKEN LINK '[[{target}]]' in {field}: {path}")

        # Bidirectional reciprocal check for 'related'
        own_title = fm.get('title', '')
        for link in (fm.get('related') or []):
            target = strip_wikilink(link)
            if target in title_to_path:
                target_path = title_to_path[target]
                target_fm, _ = pages.get(target_path, (None, None))
                if target_fm and own_title:
                    back = [strip_wikilink(l) for l in (target_fm.get('related') or [])]
                    if own_title not in back:
                        errors.append(
                            f"MISSING RECIPROCAL: '{own_title}' links to '{target}', "
                            f"but '{target}' does not list '{own_title}' in related"
                        )

        # Required body sections present
        required_sections = [
            '## How It Works',
            '## Tensions & Open Questions',
            '## See Also',
            '## Sources',
        ]
        for section in required_sections:
            if section not in body:
                errors.append(f"MISSING SECTION '{section}': {path}")

        # Sources section: each bullet referencing a vault-internal `.md` path
        # must wrap it as a wikilink, markdown link, or code span. Bare paths
        # render as plain text in Obsidian and break navigation. Heuristic: a
        # token containing at least one `/` and ending in `.md`, after stripping
        # URLs / wikilinks / markdown links / code spans.
        sources_match = re.search(
            r'^## Sources\s*\n(.*?)(?=\n## |\Z)', body, re.MULTILINE | re.DOTALL
        )
        if sources_match:
            for line in sources_match.group(1).splitlines():
                if not line.lstrip().startswith('- '):
                    continue
                residue = re.sub(r'https?://\S+', '', line)
                residue = re.sub(r'\[\[[^\]]+\]\]', '', residue)
                residue = re.sub(r'\[[^\]]*\]\([^)]+\)', '', residue)
                residue = re.sub(r'`[^`]+`', '', residue)
                if re.search(r'\S+/\S+\.md\b', residue):
                    errors.append(
                        f"BARE-PATH SOURCE (wrap as `[[filename]]`): "
                        f"{path}: {line.strip()}"
                    )

    # Summary
    if errors:
        print(f"\n{len(errors)} issue(s) found:\n")
        for e in errors:
            print(f"  {e}")
        return 1

    print(f"OK — {len(pages)} pages passed all checks.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
