#!/usr/bin/env python3
"""
Adds visual breadcrumb navigation and BreadcrumbList schema to every
existing game page. Safe to re-run - skips pages that already have it.
"""

import glob
import json
import re

DOMAIN = "https://playpixelsprout.com"


def main():
    files = glob.glob("games/*.html")
    patched = 0
    skipped = 0

    for path in files:
        with open(path, encoding="utf-8") as f:
            content = f.read()

        if 'class="breadcrumb"' in content:
            skipped += 1
            continue

        title_match = re.search(r'<h1 class="game-title">([^<]+)</h1>', content)
        meta_match = re.search(r'<div class="game-meta">([^<]+)</div>', content)
        if not title_match:
            print(f"SKIP (no title found): {path}")
            continue

        title = title_match.group(1)
        category = meta_match.group(1).strip() if meta_match else "Arcade"
        slug = path.split("/")[-1].replace(".html", "")

        breadcrumb_html = (
            f'  <div class="breadcrumb" style="font-family:\'IBM Plex Mono\',monospace;'
            f'font-size:12px;color:var(--muted);margin-bottom:8px;">\n'
            f'    <a href="../index.html" style="color:var(--teal);text-decoration:none;">Home</a>'
            f' / {category} / {title}\n'
            f'  </div>\n'
        )

        content = content.replace(
            '<div class="game-shell">\n',
            '<div class="game-shell">\n' + breadcrumb_html,
            1,
        )

        breadcrumb_schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{DOMAIN}/"},
                {"@type": "ListItem", "position": 2, "name": category, "item": f"{DOMAIN}/games/{slug}.html"},
                {"@type": "ListItem", "position": 3, "name": title, "item": f"{DOMAIN}/games/{slug}.html"},
            ],
        }
        schema_tag = f'<script type="application/ld+json">{json.dumps(breadcrumb_schema)}</script>\n'
        content = content.replace("</head>", schema_tag + "</head>", 1)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        patched += 1

    print(f"Added breadcrumbs to: {patched} pages")
    print(f"Skipped (already had it): {skipped}")


if __name__ == "__main__":
    main()
