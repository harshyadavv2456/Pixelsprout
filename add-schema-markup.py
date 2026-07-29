#!/usr/bin/env python3
"""
Adds Schema.org VideoGame structured data (JSON-LD) to every game page.

This is pure, safe, passive SEO — it tells Google explicitly "this page is
a game, here's its name/genre/thumbnail," which can improve how the page
shows up in search results (richer listings). Zero risk, zero ongoing
effort once added. Uses games-index.json (already built) to look up each
game's real thumbnail and category.

Run this once against your existing games. Also updates the daily/bulk
scripts so all future games get this automatically.
"""

import glob
import json
import re

DOMAIN = "https://playpixelsprout.com"


def load_index():
    try:
        with open("games-index.json", encoding="utf-8") as f:
            games = json.load(f)
        return {g["slug"]: g for g in games}
    except FileNotFoundError:
        print("WARNING: games-index.json not found — thumbnails will be omitted.")
        return {}


def build_schema(title, description, category, slug, thumbnail):
    schema = {
        "@context": "https://schema.org",
        "@type": "VideoGame",
        "name": title,
        "description": description,
        "genre": category,
        "url": f"{DOMAIN}/games/{slug}.html",
        "applicationCategory": "Game",
        "operatingSystem": "Web Browser",
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD",
        },
    }
    if thumbnail:
        schema["image"] = thumbnail
    return json.dumps(schema)


def main():
    index_by_slug = load_index()
    files = glob.glob("games/*.html")
    patched = 0
    skipped = 0

    for path in files:
        with open(path, encoding="utf-8") as f:
            content = f.read()

        if "application/ld+json" in content:
            skipped += 1
            continue

        title_match = re.search(r'<h1 class="game-title">([^<]+)</h1>', content)
        meta_match = re.search(r'<div class="game-meta">([^<]+)</div>', content)
        desc_match = re.search(r'<p class="how-to">([^<]+)', content)

        if not title_match:
            print(f"SKIP (no title found): {path}")
            continue

        title = title_match.group(1)
        category = meta_match.group(1).strip() if meta_match else "Arcade"
        description = desc_match.group(1).strip() if desc_match else f"Play {title} free online."
        slug = path.split("/")[-1].replace(".html", "")
        thumbnail = index_by_slug.get(slug, {}).get("thumbnail", "")

        schema_json = build_schema(title, description, category, slug, thumbnail)
        schema_tag = f'<script type="application/ld+json">{schema_json}</script>\n'

        new_content = content.replace("</head>", schema_tag + "</head>", 1)
        if new_content != content:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)
            patched += 1

    print(f"Added structured data to: {patched} pages")
    print(f"Skipped (already had it): {skipped}")


if __name__ == "__main__":
    main()
