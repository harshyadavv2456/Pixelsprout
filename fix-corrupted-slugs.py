#!/usr/bin/env python3
"""
Fixes corrupted slug values in games-index.json (e.g. "games\\baba-is-you"
instead of "baba-is-you"), which cause both broken schema URLs and the
thumbnail-lookup failures on affected game pages.

Reports exactly what it finds and fixes before making changes.
"""

import json
import re

def clean_slug(slug):
    # Strip any path-like prefix (backslash or forward slash), keep only
    # the actual final component
    cleaned = re.split(r'[\\/]', slug)[-1]
    return cleaned

def main():
    with open("games-index.json", encoding="utf-8") as f:
        games = json.load(f)

    fixed = []
    for g in games:
        original = g["slug"]
        cleaned = clean_slug(original)
        if cleaned != original:
            fixed.append((original, cleaned))
            g["slug"] = cleaned

    if not fixed:
        print("No corrupted slugs found. games-index.json is clean.")
        return

    print(f"Found and fixed {len(fixed)} corrupted slug(s):")
    for original, cleaned in fixed:
        print(f"  '{original}' -> '{cleaned}'")

    with open("games-index.json", "w", encoding="utf-8") as f:
        json.dump(games, f)

    print("\ngames-index.json updated. Next: run fix-corrupted-game-pages.py to fix the actual .html files too.")


if __name__ == "__main__":
    main()
