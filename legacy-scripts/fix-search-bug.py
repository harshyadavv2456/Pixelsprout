#!/usr/bin/env python3
"""
One-time repair script for Pixelsprout.

Fixes a real bug: the bulk import wrote game titles into the marquee ticker's
JS array using naive single-quote wrapping. Titles containing an apostrophe
(e.g. "Don't Move") broke the JavaScript string literal mid-file, which
crashed the entire inline <script> block on the page — that's why search,
the marquee ticker, and the live result count all stopped working at once.
It was one bug with several visible symptoms, not several separate bugs.

This script rebuilds that one array safely using JSON encoding (which
correctly escapes apostrophes, quotes, and anything else), and also makes
the "X games" counter next to the search box update itself on page load
instead of sitting on a stale hardcoded number.

Run this ONCE against your real index.html.
"""

import json
import re
import sys

INDEX_FILE = "index.html"


def main():
    with open(INDEX_FILE, encoding="utf-8") as f:
        html = f.read()

    # Pull every game title from the safe, properly-quoted data-name
    # attributes already sitting in the HTML (these were never broken —
    # only the separately-built marquee array was).
    titles = re.findall(r'data-name="([^"]*)"', html)
    if not titles:
        print("ERROR: couldn't find any data-name attributes — is this the right index.html?")
        sys.exit(1)

    titles_upper = [t.upper() for t in titles]
    fixed_names_line = "const names = " + json.dumps(titles_upper) + ";"

    # Replace the (broken) names array with the fixed one, no matter how
    # mangled its current contents are — anchored on the stable
    # "const names = [" start and the next known line as the end boundary.
    pattern = re.compile(r"const names = \[.*?\];(?=\s*const track)", re.DOTALL)
    if not pattern.search(html):
        print("ERROR: couldn't locate the marquee names array to replace. Aborting without changes.")
        sys.exit(1)

    html = pattern.sub(lambda m: fixed_names_line, html, count=1)

    # Make the search result counter correct from page load, not just after typing.
    if "resultCount.textContent = cards.length" not in html:
        html = html.replace(
            "const cards = Array.from(document.querySelectorAll('.card'));",
            "const cards = Array.from(document.querySelectorAll('.card'));\n"
            "  document.getElementById('result-count').textContent = cards.length + ' games';",
            1,
        )

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Fixed. Rebuilt marquee array with {len(titles)} properly-escaped titles.")
    print("Search, marquee ticker, and live result count should all work now.")


if __name__ == "__main__":
    main()
