#!/usr/bin/env python3
"""
Rebuilds the sidebar genre list to match your actual 42 category landing
pages, linking to those real pages instead of old on-page anchor links
(some of which point to categories that no longer match current data).

Safe, one-time fix. Re-run any time category pages are regenerated to
keep counts current (or just leave it - the list of qualifying categories
rarely changes once established).
"""

import json
import re

GAMES_INDEX_FILE = "games-index.json"
INDEX_FILE = "index.html"
MIN_GAMES = 15


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def main():
    with open(GAMES_INDEX_FILE, encoding="utf-8") as f:
        games = json.load(f)

    from collections import Counter
    counts = Counter(g["category"] for g in games)
    qualifying = [(c, n) for c, n in counts.most_common() if n >= MIN_GAMES]

    links = ['    <a href="/" class="sidebar-link active" data-filter="all">All Games</a>']
    for category, count in qualifying:
        slug = slugify(category)
        links.append(f'    <a href="{slug}/" class="sidebar-link">{category}</a>')

    new_nav = "  <nav class=\"sidebar-nav\">\n" + "\n".join(links) + "\n  </nav>"

    with open(INDEX_FILE, encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(r'<nav class="sidebar-nav">.*?</nav>', re.DOTALL)
    new_content, count_replaced = pattern.subn(new_nav, content, count=1)

    if count_replaced == 0:
        print("ERROR: could not find sidebar-nav block in index.html - no changes made.")
        return

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Sidebar updated with {len(qualifying)} categories, linking to real category pages.")


if __name__ == "__main__":
    main()
