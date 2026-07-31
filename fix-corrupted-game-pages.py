#!/usr/bin/env python3
"""
Fixes the actual game .html files: corrects broken "games/games\\slug.html"
style URLs in schema markup (should just be "games/slug.html"), and fills
in the correct data-thumbnail attribute from the (now-cleaned)
games-index.json. Run this AFTER fix-corrupted-slugs.py.

Safe to run on every page - only changes files that actually have the bug.
"""

import glob
import json
import re

def main():
    with open("games-index.json", encoding="utf-8") as f:
        games = json.load(f)
    thumb_by_slug = {g["slug"]: g.get("thumbnail", "") for g in games}

    url_fixed = 0
    thumb_fixed = 0

    for path in glob.glob("games/*.html"):
        with open(path, encoding="utf-8") as f:
            content = f.read()
        original = content
        slug = path.split("/")[-1].replace(".html", "")

        # Fix broken schema URLs: games/games\slug.html or games/games/slug.html -> games/slug.html
        content = re.sub(
            r'/games/games[\\/]+' + re.escape(slug) + r'\.html',
            f'/games/{slug}.html',
            content,
        )
        if content != original:
            url_fixed += 1

        # Fix data-thumbnail if empty or wrong, using the cleaned index as truth
        correct_thumb = thumb_by_slug.get(slug, "")
        if correct_thumb:
            new_content = re.sub(
                r'data-thumbnail="[^"]*"',
                f'data-thumbnail="{correct_thumb}"',
                content,
                count=1,
            )
            if new_content != content:
                content = new_content
                thumb_fixed += 1

        if content != original:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

    print(f"Fixed broken schema URLs on {url_fixed} page(s).")
    print(f"Fixed/filled thumbnail data on {thumb_fixed} page(s).")


if __name__ == "__main__":
    main()
