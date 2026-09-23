#!/usr/bin/env python3
"""
Removes the hardcoded screen.orientation.lock('landscape') call from every
existing embedded game page's fullscreen button.

Root cause: the fullscreen button was built assuming every game wants
landscape. Some GamePix games are actually designed for portrait play —
forcing them into landscape broke their own internal fullscreen/rotation
logic, which is worse than not locking orientation at all.

Since we don't have reliable per-game orientation data for games already
added (that info wasn't captured at the time), the safe fix is to stop
forcing an orientation at all on existing pages — let the browser/game
decide naturally. New games added going forward DO capture the correct
per-game orientation from GamePix's own data and lock correctly (see the
updated auto-add-games.py / bulk-add-games.py templates).
"""

import glob
import re

ORIENTATION_LOCK_PATTERN = re.compile(
    r"\s*if \(screen\.orientation && screen\.orientation\.lock\) \{\s*"
    r"screen\.orientation\.lock\('landscape'\)\.catch\(\(\) => \{\}\);\s*"
    r"\}",
)


def main():
    files = glob.glob("games/*.html")
    patched = 0
    skipped = 0

    for path in files:
        with open(path, encoding="utf-8") as f:
            content = f.read()

        if "screen.orientation.lock" not in content:
            skipped += 1
            continue

        new_content = ORIENTATION_LOCK_PATTERN.sub("", content)
        if new_content != content:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)
            patched += 1

    print(f"Removed forced landscape lock from: {patched} pages")
    print(f"Skipped (no lock present, e.g. your 8 original games): {skipped}")


if __name__ == "__main__":
    main()
