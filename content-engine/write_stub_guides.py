#!/usr/bin/env python3
"""
Rewrites every guide page on content-engine/noindex-guides.json as a short, true stub
(game name, plays free in the browser on Pixelsprout, link to the game page) with
<meta name="robots" content="noindex,follow">, then lets seo_cleanup.py drop them
from sitemap.xml. Only run this by hand when URLs are added to the list; the daily
pipeline never regenerates listed pages.

Usage: python content-engine/write_stub_guides.py [--only <slug> ...]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_guides as gg  # noqa: E402
import noindex_guides  # noqa: E402
import page_renderer as render  # noqa: E402
import seo_cleanup  # noqa: E402
import similar_games as sim  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    args = ap.parse_args()
    urls = noindex_guides.load_urls()
    all_games = gg.load_json(gg.GAMES_INDEX_PATH, [])
    sim.build_index(all_games)
    written = 0
    for game in all_games:
        if args.only and game["slug"] not in args.only:
            continue
        page_urls = gg.guide_urls_for(game)
        todo = [p for p, u in page_urls.items() if u in urls]
        if not todo:
            continue
        related = sim.find_similar(game, all_games, limit=8)
        category_url = gg.category_url_for(game)
        for page_type in todo:
            page_html = render.render_stub_page(page_type, game, related, page_urls, category_url)
            page_html, _ = seo_cleanup.set_noindex(page_html, True)
            out = os.path.join(gg.REPO_ROOT, page_urls[page_type].strip("/"), "index.html")
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "w", encoding="utf-8", newline="\n") as f:
                f.write(page_html)
            written += 1
    print(f"Stub guide pages written: {written}")


if __name__ == "__main__":
    main()
