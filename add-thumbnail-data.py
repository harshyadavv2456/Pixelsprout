#!/usr/bin/env python3
"""
Fixes the wrong-thumbnail bug by embedding each game's correct thumbnail
directly on its own page, sourced from games-index.json (the reliable
source of truth), eliminating the previous wrong-source risk entirely.
"""

import glob
import json
import re

def main():
    with open("games-index.json", encoding="utf-8") as f:
        games = json.load(f)
    thumb_by_slug = {g["slug"]: g.get("thumbnail", "") for g in games}

    patched = 0
    skipped = 0
    for path in glob.glob("games/*.html"):
        with open(path, encoding="utf-8") as f:
            content = f.read()

        if 'data-thumbnail=' in content:
            skipped += 1
            continue

        slug = path.split("/")[-1].replace(".html", "")
        thumbnail = thumb_by_slug.get(slug, "")

        new_content = content.replace(
            '<div class="game-shell">',
            f'<div class="game-shell" data-thumbnail="{thumbnail}">',
            1,
        )
        if new_content != content:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)
            patched += 1

    print(f"Added correct thumbnail data to {patched} pages.")
    print(f"Skipped (already had it): {skipped}")


if __name__ == "__main__":
    main()
