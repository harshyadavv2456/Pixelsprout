#!/usr/bin/env python3
"""
Adds Pinterest's domain verification meta tag to index.html.
Safe, minimal, single-line insertion right after <head> — doesn't touch
or depend on anything else in the file.
"""

PINTEREST_TAG = '<meta name="p:domain_verify" content="119e6733e3c5887bb3f24d440ab498fa"/>\n'

with open("index.html", encoding="utf-8") as f:
    content = f.read()

if "p:domain_verify" in content:
    print("Already present — no changes made.")
else:
    new_content = content.replace("<head>", "<head>\n" + PINTEREST_TAG, 1)
    if new_content == content:
        print("ERROR: couldn't find <head> tag — no changes made. Check index.html manually.")
    else:
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Pinterest verification tag added successfully.")
