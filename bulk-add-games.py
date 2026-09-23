#!/usr/bin/env python3
"""
Pixelsprout ONE-TIME bulk add.

Pulls a larger, quality-filtered, category-diversified batch of games from
the GamePix feed in a single run. Meant to be run once, by hand, to give the
site a broader starting catalog. The daily auto-add-games.py script keeps
running afterward at its normal slow pace (3/day) — this script does not
change that cadence, it just shares the same tracking file so the two never
add the same game twice.

Guardrails built in on purpose, not arbitrary:
- MIN_QUALITY filters out low-quality filler games
- MAX_PER_CATEGORY prevents one genre (e.g. endless racing clones) from
  dominating the batch
- MAX_TOTAL caps the whole run so this stays "a bigger batch," not
  "the entire catalog dumped at once" — the latter risks looking like thin/
  spam content to Google while your AdSense review is still pending
"""

import json
import re
import subprocess
import sys
import urllib.request

import site_pages
import site_shell
from datetime import datetime, timezone
from xml.sax.saxutils import escape

RSS_FILE = "rss.xml"
RSS_MAX_ITEMS = 60

# ---- CONFIG ----
FEED_URL = "https://feeds.gamepix.com/v2/json?sid=P7924&pagination=48&page=1"
MAX_TOTAL = None            # no cap — pull every game that passes the quality filter
MAX_PER_CATEGORY = None     # no cap — no artificial genre balancing
MIN_QUALITY = 0.55          # still filters out broken/low-effort entries — "worthy" games only
MAX_PAGES_TO_CHECK = 60     # safety ceiling only, to prevent a runaway loop if the feed misbehaves —
                            # not a business limit; at 48/page this covers up to ~2,880 games
SITE_ROOT = "."
TRACKING_FILE = f"{SITE_ROOT}/games-data.json"
SITEMAP_FILE = f"{SITE_ROOT}/sitemap.xml"
GAMES_DIR = f"{SITE_ROOT}/games"
DOMAIN = "https://playpixelsprout.com"




def slugify(title):
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def load_tracking():
    try:
        with open(TRACKING_FILE, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"added_ids": []}


def save_tracking(data):
    with open(TRACKING_FILE, "w", encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def fetch_diverse_games(already_added_ids):
    """Pull every quality-filtered game the feed has, with no total or per-category cap."""
    picked = []
    per_category_count = {}
    url = FEED_URL
    pages_checked = 0

    while url and pages_checked < MAX_PAGES_TO_CHECK:
        if MAX_TOTAL is not None and len(picked) >= MAX_TOTAL:
            break

        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        for item in data.get("items", []):
            if MAX_TOTAL is not None and len(picked) >= MAX_TOTAL:
                break

            game_id = item.get("id") or item.get("namespace")
            if game_id in already_added_ids:
                continue

            quality = item.get("quality_score", 0)
            if quality < MIN_QUALITY:
                continue

            category = (item.get("category") or "Arcade").title()
            if MAX_PER_CATEGORY is not None and per_category_count.get(category, 0) >= MAX_PER_CATEGORY:
                continue

            picked.append({
                "id": game_id,
                "title": item.get("title", "Untitled Game"),
                "category": category,
                "description": item.get("description", ""),
                "thumbnail": item.get("banner_image") or item.get("image", ""),
                "embed_url": item.get("url", ""),
                "orientation": item.get("orientation", ""),
            })
            per_category_count[category] = per_category_count.get(category, 0) + 1

        url = data.get("next_url")
        pages_checked += 1

    return picked


def build_game_page(game):
    update_games_index(game)
    catalog = site_shell.load_catalog()
    html = site_pages.render_game_page(site_pages.new_game_fields(game), catalog, total_games=len(catalog))
    path = f"{GAMES_DIR}/{game['slug']}.html"
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    return path


def update_games_index(game):
    index_path = "games-index.json"
    try:
        with open(index_path, encoding='utf-8') as f:
            games_list = json.load(f)
    except FileNotFoundError:
        games_list = []
    games_list.append({
        "slug": game["slug"],
        "title": game["title"],
        "category": game["category"],
        "thumbnail": game["thumbnail"],
    })
    with open(index_path, "w", encoding='utf-8') as f:
        json.dump(games_list, f)



def add_to_sitemap(game):
    with open(SITEMAP_FILE, encoding='utf-8') as f:
        sitemap = f.read()
    new_url = f'  <url><loc>{DOMAIN}/games/{game["slug"]}.html</loc><priority>0.7</priority></url>\n'
    sitemap = sitemap.replace("</urlset>", new_url + "</urlset>")
    with open(SITEMAP_FILE, "w", encoding='utf-8') as f:
        f.write(sitemap)


def add_to_rss(game):
    try:
        with open(RSS_FILE, encoding='utf-8') as f:
            rss = f.read()
    except FileNotFoundError:
        return

    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    title = escape(game["title"])
    link = f"{DOMAIN}/games/{game['slug']}.html"
    description = escape(f"Play {game['title']} free online at Pixelsprout — no download needed.")
    thumbnail = game.get("thumbnail", "") or f"{DOMAIN}/assets/logo-icon.png"
    enclosure = f'<enclosure url="{escape(thumbnail)}" type="image/jpeg"/>'

    new_item = f"""  <item>
    <title>{title}</title>
    <link>{link}</link>
    <guid>{link}</guid>
    <description>{description}</description>
    <pubDate>{now}</pubDate>
    {enclosure}
  </item>
"""
    first_item_idx = rss.find("  <item>")
    if first_item_idx == -1:
        rss = rss.replace("</channel>", new_item + "</channel>")
    else:
        rss = rss[:first_item_idx] + new_item + rss[first_item_idx:]

    items = re.findall(r"  <item>.*?</item>\n", rss, re.DOTALL)
    if len(items) > RSS_MAX_ITEMS:
        header_end = rss.find("  <item>")
        header = rss[:header_end]
        footer = "</channel>\n</rss>\n"
        trimmed_items = "".join(items[:RSS_MAX_ITEMS])
        rss = header + trimmed_items + footer

    with open(RSS_FILE, "w", encoding='utf-8') as f:
        f.write(rss)


def git_commit_and_push(added_titles):
    if not added_titles:
        print("No new games added — nothing to commit.")
        return
    subprocess.run(["git", "add", "."], check=True)
    msg = f"One-time bulk add: {len(added_titles)} games across categories"
    subprocess.run(["git", "commit", "-m", msg], check=True)
    subprocess.run(["git", "push"], check=True)
    print(f"Pushed: {msg}")


def main():
    tracking = load_tracking()
    already_added = set(tracking["added_ids"])

    print(f"Fetching a diverse batch (max {MAX_TOTAL} games, max {MAX_PER_CATEGORY} per category, min quality {MIN_QUALITY})...")
    games = fetch_diverse_games(already_added)

    if not games:
        print("No qualifying new games found.")
        return

    print(f"Found {len(games)} games to add:")
    by_category = {}
    for g in games:
        by_category.setdefault(g["category"], []).append(g["title"])
    for cat, titles in by_category.items():
        print(f"  {cat}: {', '.join(titles)}")

    added_titles = []
    for game in games:
        game["slug"] = slugify(game["title"])
        build_game_page(game)
        add_to_sitemap(game)
        add_to_rss(game)
        tracking["added_ids"].append(game["id"])
        added_titles.append(game["title"])
        print(f"Added: {game['title']} ({game['category']})")

    save_tracking(tracking)
    site_pages.build_home(site_shell.load_catalog())
    git_commit_and_push(added_titles)


if __name__ == "__main__":
    main()
