#!/usr/bin/env python3
"""
Patches index.html in place: adds loading="lazy" to every homepage game
card's thumbnail image. This is what's actually making the homepage slow
right now - every card image was set to load eagerly, so the browser
tries to fetch thousands of thumbnails the instant the page loads,
regardless of whether they're visible on screen.

Pure local find-and-replace, no content changes, no Groq, no GitHub
Actions - same category of fix as fix_alignment_locally.py. Safe to run
repeatedly (idempotent via regex negative-lookbehind - never double-adds
the attribute).

Usage (from repo root):
  python fix_lazy_loading_locally.py

Then:
  git add index.html
  git commit -m "Add lazy-loading to homepage card images (fixes slow load)"
  git push
"""

import re

MARKER = 'style="width:100%; height:100%; object-fit:cover; border-radius:9px;"'
LAZY_PREFIX = 'loading="lazy" '

# Only matches MARKER occurrences NOT already preceded by loading="lazy " -
# makes this safe to run more than once without stacking the attribute.
PATTERN = re.compile(r'(?<!' + re.escape(LAZY_PREFIX) + r')' + re.escape(MARKER))


def main():
    with open("index.html", encoding="utf-8") as f:
        content = f.read()

    total = len(re.findall(re.escape(MARKER), content))
    already_lazy = len(re.findall(re.escape(LAZY_PREFIX + MARKER), content))
    print(f"Found {total} homepage card images total, {already_lazy} already lazy-loaded.")

    new_content, n = PATTERN.subn(LAZY_PREFIX + MARKER, content)

    if n == 0:
        print("Nothing to do - already patched.")
        return

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f'Patched {n} card images to loading="lazy".')
    print("Now run:")
    print("  git add index.html")
    print('  git commit -m "Add lazy-loading to homepage card images (fixes slow load)"')
    print("  git push")


if __name__ == "__main__":
    main()
