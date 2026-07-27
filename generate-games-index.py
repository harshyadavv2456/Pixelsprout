#!/usr/bin/env python3
"""
Generates games-index.json — a lightweight (not the full multi-MB HTML)
list of {slug, title, category, thumbnail} for every game currently on the
site. Individual game pages fetch this small file (not the whole homepage)
to render "similar games" recommendations without a heavy performance cost.

Run this once now. auto-add-games.py and bulk-add-games.py have been
updated to keep this file in sync automatically going forward.
"""

import json
import re

INDEX_FILE = "index.html"
OUTPUT_FILE = "games-index.json"


def main():
    with open(INDEX_FILE, encoding="utf-8") as f:
        html = f.read()

    # Walk through category sections, associating each card with the
    # category heading it falls under.
    section_pattern = re.compile(
        r'<h2>([^<]+)</h2>.*?<div[^>]*class="grid"[^>]*data-grid[^>]*>(.*?)</div>\s*(?=(?:<div|<p id="no-results"))',
        re.DOTALL,
    )

    games = []
    seen_slugs = set()

    for category, grid_html in section_pattern.findall(html):
        if category.strip() == "Popular Picks":
            continue  # these are clones of real games elsewhere, skip to avoid duplicates

        card_pattern = re.compile(
            r'<a class="card[^"]*" href="games/([^"]+)\.html"[^>]*>(.*?)</a>',
            re.DOTALL,
        )
        for slug, card_inner in card_pattern.findall(grid_html):
            if slug in seen_slugs:
                continue
            title_match = re.search(r'<h3>([^<]+)</h3>', card_inner)
            thumb_match = re.search(r'<img[^>]*src="([^"]+)"', card_inner)
            if not title_match:
                continue
            games.append({
                "slug": slug,
                "title": title_match.group(1),
                "category": category.strip(),
                "thumbnail": thumb_match.group(1) if thumb_match else "",
            })
            seen_slugs.add(slug)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(games, f)

    print(f"Wrote {OUTPUT_FILE} with {len(games)} games.")


if __name__ == "__main__":
    main()
