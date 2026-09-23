#!/usr/bin/env python3
"""
One-time local fix: reorders the cards ALREADY LIVE in index.html so that
GamePix games (your original catalog) come first in every category, and
GameMonetize games (which show more visible ads/branding in the embed)
come after. This is what the insertion-order bug (now fixed in all 4
add-games scripts) should have done from the start - this script cleans
up the games already added before that fix landed.

Pure local reorder - no content changes, no new games, no Groq, no
GitHub Actions. Cross-references games-index.json (which has the
"source" field) to know which slug belongs to which source. Safe to run
repeatedly (idempotent - reordering an already-correctly-ordered grid is
a no-op).

Usage (from repo root):
  python reorder_cards_by_source_locally.py

Then:
  git add index.html
  git commit -m "Reorder homepage: GamePix games first, GameMonetize after"
  git push
"""

import json
import re

with open("games-index.json", encoding="utf-8") as f:
    catalog = json.load(f)

# Anything without an explicit "source" field is an original GamePix
# entry (that field was only added once GameMonetize entries started
# being tagged).
SLUG_SOURCE = {g["slug"]: g.get("source", "gamepix") for g in catalog}

CARD_PATTERN = re.compile(
    r'    <a class="card" href="games/([^"]+)\.html".*?</a>\r?\n',
    re.DOTALL,
)


def reorder_grid(grid_content):
    blocks_by_slug_order = [(m.group(1), m.group(0)) for m in CARD_PATTERN.finditer(grid_content)]

    gamepix_blocks = [b for slug, b in blocks_by_slug_order if SLUG_SOURCE.get(slug, "gamepix") != "gamemonetize"]
    gamemonetize_blocks = [b for slug, b in blocks_by_slug_order if SLUG_SOURCE.get(slug, "gamepix") == "gamemonetize"]

    if not gamemonetize_blocks:
        return grid_content, False  # nothing to reorder in this category

    # Anything that isn't a card (shouldn't be any inside a grid, but stay safe)
    non_card_leftover = CARD_PATTERN.sub("", grid_content)

    new_content = "".join(gamepix_blocks) + "".join(gamemonetize_blocks) + non_card_leftover
    return new_content, True


def main():
    with open("index.html", encoding="utf-8") as f:
        index_html = f.read()

    # Split the file into per-category grid regions and reorder each one independently.
    grid_pattern = re.compile(r'<div class="grid" data-grid>\r?\n(.*?)(?=\r?\n  <div id="[a-z0-9-]*" class="category |\r?\n  <p id="no-results")', re.DOTALL)

    categories_changed = 0

    def replace_grid(m):
        nonlocal categories_changed
        grid_content = m.group(1)
        new_content, changed = reorder_grid(grid_content)
        if changed:
            categories_changed += 1
        return f'<div class="grid" data-grid>\n{new_content}'

    new_index_html = grid_pattern.sub(replace_grid, index_html)

    if categories_changed == 0:
        print("Nothing to reorder - either already correct, or no GameMonetize games found in any category grid.")
        return

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_index_html)

    print(f"Reordered {categories_changed} categories - GamePix games now appear before GameMonetize games in each.")
    print("Now run:")
    print("  git add index.html")
    print('  git commit -m "Reorder homepage: GamePix games first, GameMonetize after"')
    print("  git push")


if __name__ == "__main__":
    main()
