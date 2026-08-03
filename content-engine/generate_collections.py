#!/usr/bin/env python3
"""
Generates /games-like/<slug>/ pages from content-engine/collections_data.py.
Safe to re-run any time (e.g. after new games are added) - it always
rebuilds each collection from the current catalog, so a newly-added game
that matches an existing collection's keywords will show up automatically
next run.

Usage:
  python content-engine/generate_collections.py
  python content-engine/generate_collections.py --dry-run
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from groq_client import GroqRotatingClient
import fallback_content as fb
import similar_games as sim
import page_renderer as render
from collections_data import COLLECTIONS

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAMES_INDEX_PATH = os.path.join(REPO_ROOT, "games-index.json")
SITEMAP_PATH = os.path.join(REPO_ROOT, "sitemap.xml")


def load_json(path, default):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default


def update_sitemap(new_urls):
    if not new_urls:
        return
    with open(SITEMAP_PATH, encoding="utf-8") as f:
        content = f.read()
    existing = set()
    for url in new_urls:
        if f"<loc>https://playpixelsprout.com{url}</loc>" in content:
            existing.add(url)
    to_add = [u for u in new_urls if u not in existing]
    if not to_add:
        return
    entries = "\n".join(f"  <url><loc>https://playpixelsprout.com{u}</loc><priority>0.6</priority></url>" for u in to_add)
    content = content.replace("</urlset>", entries + "\n</urlset>") if "</urlset>" in content else content + "\n" + entries
    with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    all_games = load_json(GAMES_INDEX_PATH, [])
    if not all_games:
        print("games-index.json not found or empty.")
        return

    client = GroqRotatingClient()
    if not args.dry_run and not client.has_keys:
        print("No GROQ_API_KEY_1..5 found - running in fallback mode.")

    new_urls = []
    for coll in COLLECTIONS:
        matches = sim.find_by_keywords(
            all_games,
            category_keywords=coll.get("category_keywords"),
            title_keywords=coll.get("title_keywords"),
            limit=20,
        )
        if len(matches) < 4:
            print(f"SKIP {coll['slug']}: only {len(matches)} matches, too few to publish")
            continue

        if not args.dry_run and client.has_keys:
            system = (
                "You write concise, genuine intro copy for a free browser games site. "
                "Respond with ONLY a JSON object, no markdown, no commentary."
            )
            user = (
                f'Write JSON: {{"intro": "2-3 sentences introducing a page of free browser games '
                f'similar to {coll["display_name"]}, for someone who searched for that game but wants '
                f'to play something free right now, no download or account needed."}}.'
            )
            content = client.generate_json(system, user)
            if not content:
                content = fb.fallback_collection_intro(coll["display_name"])
            time.sleep(1.5)
        else:
            content = fb.fallback_collection_intro(coll["display_name"])

        out_dir = os.path.join(REPO_ROOT, "games-like", coll["slug"])
        os.makedirs(out_dir, exist_ok=True)
        html = render.render_collection_page(coll, matches, content)
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)

        new_urls.append(f"/games-like/{coll['slug']}/")
        print(f"OK {coll['slug']}: {len(matches)} games")

    update_sitemap(new_urls)
    print(f"\nDone. {len(new_urls)} collection pages generated.")


if __name__ == "__main__":
    main()
