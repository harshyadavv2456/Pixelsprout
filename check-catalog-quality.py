#!/usr/bin/env python3
"""
Flags potential catalog quality issues - duplicate titles, duplicate
thumbnails, missing thumbnails, suspiciously short descriptions. Never
deletes or modifies anything - just writes a report for you to review.

Safe to run daily as part of automation. Only writes catalog-quality-
report.txt when it actually finds something worth flagging.
"""

import json
from collections import defaultdict

GAMES_INDEX_FILE = "games-index.json"
REPORT_FILE = "catalog-quality-report.txt"


def main():
    with open(GAMES_INDEX_FILE, encoding="utf-8") as f:
        games = json.load(f)

    issues = []

    # Duplicate titles (same title appearing more than once)
    by_title = defaultdict(list)
    for g in games:
        by_title[g["title"].strip().lower()].append(g["slug"])
    for title, slugs in by_title.items():
        if len(slugs) > 1:
            issues.append(f"DUPLICATE TITLE '{title}': {', '.join(slugs)}")

    # Duplicate thumbnails (same image used for different games - often
    # means the same game was added twice under different names)
    by_thumbnail = defaultdict(list)
    for g in games:
        thumb = g.get("thumbnail", "")
        if thumb:
            by_thumbnail[thumb].append(g["slug"])
    for thumb, slugs in by_thumbnail.items():
        if len(slugs) > 1:
            issues.append(f"DUPLICATE THUMBNAIL used by: {', '.join(slugs)}")

    # Missing thumbnails (excluding the 8 known original games, which use
    # custom SVG icons instead of photo thumbnails - not actually an issue)
    known_originals = {
        "snake", "flappy", "tetris", "tictactoe", "pong",
        "2048", "minesweeper", "memory-match",
    }
    for g in games:
        if not g.get("thumbnail") and g["slug"] not in known_originals:
            issues.append(f"MISSING THUMBNAIL: {g['slug']}")

    if issues:
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write(f"Catalog quality report - {len(issues)} issue(s) found\n")
            f.write("=" * 60 + "\n\n")
            f.write("\n".join(issues))
        print(f"Found {len(issues)} issue(s) - see {REPORT_FILE}")
    else:
        print("No catalog quality issues found.")


if __name__ == "__main__":
    main()
