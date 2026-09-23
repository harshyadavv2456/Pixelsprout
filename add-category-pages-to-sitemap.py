#!/usr/bin/env python3
"""
Adds every top-level page folder (genre pages, /all-games/, tool pages) to
sitemap.xml. Run right after generate-category-pages.py.

Also repairs entries written by the old version of this script on Windows,
where glob() returned "action\\" and produced URLs like /action\\/.
"""

import glob
import os

DOMAIN = "https://playpixelsprout.com"
SKIP = {"games", "assets", ".github", "api", "content-engine", "legacy-scripts", "node_modules", "qa", "qa-screenshots"}

with open("sitemap.xml", encoding="utf-8") as f:
    sitemap = f.read()

repaired = sitemap.count("\\/</loc>")
sitemap = sitemap.replace("\\/</loc>", "/</loc>")

slugs = sorted(
    os.path.basename(os.path.normpath(d)) for d in glob.glob("*/")
    if os.path.exists(os.path.join(d, "index.html"))
)
slugs = [s for s in slugs if s not in SKIP]

added = 0
for slug in slugs:
    if f"{DOMAIN}/{slug}/</loc>" not in sitemap:
        url = f"  <url><loc>{DOMAIN}/{slug}/</loc><priority>0.6</priority></url>\n"
        sitemap = sitemap.replace("</urlset>", url + "</urlset>")
        added += 1

with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write(sitemap)

print(f"Added {added} page folders to sitemap.xml, repaired {repaired} malformed entries")
