#!/usr/bin/env python3
"""
Generates dedicated landing pages for your best-populated categories
(15+ games each - anything smaller risks looking like thin content to
Google, which can hurt rather than help SEO).

Each page lives at /{category-slug}/index.html, served by Vercel at a
clean URL like playpixelsprout.com/arcade/ automatically.

Purely additive: creates new files only, never touches index.html, game
pages, or anything else already working.

Run this once now. Re-run any time your catalog grows meaningfully (e.g.
monthly) to pick up newly-qualifying categories and keep game counts
current - safe to re-run, overwrites only its own generated pages.
"""

import json
import re

DOMAIN = "https://playpixelsprout.com"
MIN_GAMES = 15
GAMES_INDEX_FILE = "games-index.json"

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" href="../favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="../assets/favicon-32x32.png">
<link rel="canonical" href="{canonical_url}">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="stylesheet" href="../styles.css">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8466016918717424" crossorigin="anonymous"></script>
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical_url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{DOMAIN}/assets/og-banner.jpg">
<script type="application/ld+json">{breadcrumb_schema}</script>
<style>
  .category-page {{ max-width: 1100px; margin: 0 auto; padding: 24px; }}
  .breadcrumb {{ font-family: 'IBM Plex Mono', monospace; font-size: 13px; color: var(--muted); margin-bottom: 16px; }}
  .breadcrumb a {{ color: var(--teal); text-decoration: none; }}
  .category-intro {{ margin-bottom: 24px; }}
  .category-intro h1 {{ font-family: 'Press Start 2P', monospace; font-size: 22px; margin-bottom: 12px; }}
  .category-intro p {{ color: var(--muted); font-size: 14px; line-height: 1.7; max-width: 700px; }}
  .category-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 10px; }}
</style>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-VTNJRV4WG8"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-VTNJRV4WG8');
</script>
</head>
<body>
<header class="site-header">
  <a class="logo" href="../index.html">
    <img class="logo-mark" src="../assets/logo-icon.png" alt="">
    <span class="logo-word">PIXELSPROUT</span>
  </a>
</header>

<div class="category-page">
  <div class="breadcrumb">
    <a href="../index.html">Home</a> / {category}
  </div>

  <div class="category-intro">
    <h1>{category} Games</h1>
    <p>{intro_copy}</p>
  </div>

  <div class="category-grid">
{cards}
  </div>
</div>

<footer class="site-footer">
  <span>© Pixelsprout — Play. Grow. Explore. Some games provided via GamePix.</span>
  <span><a href="../about.html">About</a> · <a href="../contact.html">Contact</a> · <a href="../privacy.html">Privacy</a> · <a href="../terms.html">Terms</a></span>
</footer>
</body>
</html>
"""

CARD_TEMPLATE = """    <a class="card" href="../games/{slug}.html">
      <span class="icon-tile gold" style="padding:0; overflow:hidden;">
        <img src="{thumbnail}" alt="" style="width:100%; height:100%; object-fit:cover; border-radius:9px;" loading="lazy">
      </span>
      <div class="card-body">
        <h3>{title}</h3>
      </div>
    </a>"""


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def intro_for(category, count):
    return (
        f"Browse {count} free {category.lower()} games, playable instantly in your browser. "
        f"No downloads, no accounts, no waiting — just click and play. New {category.lower()} "
        f"games are added regularly, so check back for more."
    )


def main():
    with open(GAMES_INDEX_FILE, encoding="utf-8") as f:
        games = json.load(f)

    by_category = {}
    for g in games:
        by_category.setdefault(g["category"], []).append(g)

    qualifying = {c: gs for c, gs in by_category.items() if len(gs) >= MIN_GAMES}
    print(f"{len(qualifying)} categories qualify (15+ games).")

    for category, game_list in qualifying.items():
        slug = slugify(category)
        canonical_url = f"{DOMAIN}/{slug}/"
        title = f"{category} Games - Free Online, No Download | Pixelsprout"
        description = f"Play {len(game_list)} free {category.lower()} games online at Pixelsprout. No downloads, no accounts - instant browser play."

        breadcrumb_schema = json.dumps({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{DOMAIN}/"},
                {"@type": "ListItem", "position": 2, "name": category, "item": canonical_url},
            ],
        })

        cards_html = "\n".join(
            CARD_TEMPLATE.format(
                slug=g["slug"],
                thumbnail=g.get("thumbnail") or f"{DOMAIN}/assets/logo-icon.png",
                title=g["title"],
            )
            for g in game_list
        )

        page_html = PAGE_TEMPLATE.format(
            canonical_url=canonical_url,
            title=title,
            description=description,
            DOMAIN=DOMAIN,
            breadcrumb_schema=breadcrumb_schema,
            category=category,
            intro_copy=intro_for(category, len(game_list)),
            cards=cards_html,
        )

        import os
        os.makedirs(slug, exist_ok=True)
        with open(f"{slug}/index.html", "w", encoding="utf-8") as f:
            f.write(page_html)
        print(f"Generated /{slug}/ ({len(game_list)} games)")

    print("\nDone. Add these new folders to sitemap.xml manually, or tell Claude to add a script for that too.")


if __name__ == "__main__":
    main()
