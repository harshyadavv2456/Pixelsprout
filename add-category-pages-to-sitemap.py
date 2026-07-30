#!/usr/bin/env python3
"""
Adds the 42 generated category pages to sitemap.xml. Run this once, right
after generate-category-pages.py, so Google can discover these new pages.
"""

import glob
import re

DOMAIN = "https://playpixelsprout.com"

with open("sitemap.xml", encoding="utf-8") as f:
    sitemap = f.read()

category_slugs = [
    d.rstrip("/") for d in glob.glob("*/")
    if (d.rstrip("/") + "/index.html") and __import__("os").path.exists(d + "index.html")
    and d.rstrip("/") not in ("games", "assets", ".github")
]

added = 0
for slug in category_slugs:
    url = f'  <url><loc>{DOMAIN}/{slug}/</loc><priority>0.6</priority></url>\n'
    if f"{DOMAIN}/{slug}/</loc>" not in sitemap:
        sitemap = sitemap.replace("</urlset>", url + "</urlset>")
        added += 1

with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write(sitemap)

print(f"Added {added} category pages to sitemap.xml")
