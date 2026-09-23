#!/usr/bin/env python3
"""
Pixelsprout auto-add script.

Fetches new games from a GamePix RSS/JSON feed, builds a page for each,
adds a homepage card, updates the sitemap, and commits the changes.

Designed to run unattended (e.g. via GitHub Actions on a weekly schedule).
Adds a small, capped number of games per run — intentionally NOT "everything
available" — to protect content quality and avoid looking like a thin/spam
site during AdSense review and beyond.
"""

import argparse
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
INDEXNOW_KEY = "09266bfbb51ba867175e9483e9d5fa6d"

# ---- CONFIG — fill in FEED_URL before first run ----
FEED_URL = "https://feeds.gamepix.com/v2/json?sid=P7924&pagination=12&page=1"
GAMES_PER_RUN = 3
MAX_PAGES_TO_CHECK = 5
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


def fetch_new_games(already_added_ids, games_per_run=GAMES_PER_RUN, max_pages=MAX_PAGES_TO_CHECK):
    found = []
    url = FEED_URL
    pages_checked = 0

    while url and len(found) < games_per_run and pages_checked < max_pages:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        for item in data.get("items", []):
            game_id = item.get("id") or item.get("namespace")
            if game_id in already_added_ids:
                continue
            found.append({
                "id": game_id,
                "title": item.get("title", "Untitled Game"),
                "category": (item.get("category") or "Arcade").title(),
                "description": item.get("description", ""),
                "thumbnail": item.get("banner_image") or item.get("image", ""),
                "embed_url": item.get("url", ""),
                "orientation": item.get("orientation", ""),
            })
            if len(found) >= games_per_run:
                break

        url = data.get("next_url")
        pages_checked += 1

    return found


def build_game_page(game):
    update_games_index(game)
    catalog = site_shell.load_catalog()
    html = site_pages.render_game_page(site_pages.new_game_fields(game), catalog, total_games=len(catalog))
    path = f"{GAMES_DIR}/{game['slug']}.html"
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    return path


def update_games_index(game):
    """Keep games-index.json (used for similar-games recommendations) in
    sync as new games are added, without needing to re-run the generator."""
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
    """Keep rss.xml current so dlvr.it (or any RSS reader) picks up newly
    added games automatically. Prepends the new game with a real, accurate
    timestamp, and trims the feed to the most recent RSS_MAX_ITEMS so the
    file doesn't grow unbounded as the catalog grows."""
    try:
        with open(RSS_FILE, encoding='utf-8') as f:
            rss = f.read()
    except FileNotFoundError:
        print("rss.xml not found — skipping RSS update (run generate-rss-feed.py once first).")
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

    # Insert the new item right after the opening <channel> metadata (before
    # the first existing <item>), so it's treated as the newest entry.
    first_item_idx = rss.find("  <item>")
    if first_item_idx == -1:
        rss = rss.replace("</channel>", new_item + "</channel>")
    else:
        rss = rss[:first_item_idx] + new_item + rss[first_item_idx:]

    # Trim to the most recent RSS_MAX_ITEMS items
    items = re.findall(r"  <item>.*?</item>\n", rss, re.DOTALL)
    if len(items) > RSS_MAX_ITEMS:
        header_end = rss.find("  <item>")
        header = rss[:header_end]
        footer = "</channel>\n</rss>\n"
        trimmed_items = "".join(items[:RSS_MAX_ITEMS])
        rss = header + trimmed_items + footer

    with open(RSS_FILE, "w", encoding='utf-8') as f:
        f.write(rss)


def ping_indexnow(urls):
    """Tell Bing/Yandex (and increasingly Google) about new/updated pages
    immediately, instead of waiting for their crawler's own schedule.
    Never blocks or fails the main run — this is a nice-to-have signal,
    not a critical step."""
    try:
        payload = json.dumps({
            "host": "playpixelsprout.com",
            "key": INDEXNOW_KEY,
            "keyLocation": f"{DOMAIN}/{INDEXNOW_KEY}.txt",
            "urlList": urls,
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://api.indexnow.org/indexnow",
            data=payload,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"IndexNow: notified {len(urls)} URL(s), status {resp.status}")
    except Exception as e:
        print(f"IndexNow ping failed (non-critical, continuing): {e}")


def git_commit_and_push(added_titles):
    if not added_titles:
        print("No new games added — nothing to commit.")
        return
    subprocess.run(["git", "add", "."], check=True)
    msg = "Auto-add games: " + ", ".join(added_titles)
    subprocess.run(["git", "commit", "-m", msg], check=True)
    subprocess.run(["git", "push"], check=True)
    print(f"Pushed: {msg}")


def main():
    parser = argparse.ArgumentParser(description="Add new games to Pixelsprout from the GamePix feed.")
    parser.add_argument("--count", type=int, default=GAMES_PER_RUN,
                         help=f"How many new games to add this run (default: {GAMES_PER_RUN}, the safe daily pace).")
    parser.add_argument("--max-pages", type=int, default=MAX_PAGES_TO_CHECK,
                         help=f"How many feed pages to check while looking for new games (default: {MAX_PAGES_TO_CHECK}).")
    args = parser.parse_args()

    if FEED_URL.startswith("PASTE_"):
        print("ERROR: set FEED_URL in this script before running.")
        sys.exit(1)

    tracking = load_tracking()
    already_added = set(tracking["added_ids"])

    new_games = fetch_new_games(already_added, games_per_run=args.count, max_pages=args.max_pages)
    if not new_games:
        print("No new games found this run.")
        return

    added_titles = []
    new_urls = []
    for game in new_games:
        game["slug"] = slugify(game["title"])
        build_game_page(game)
        add_to_sitemap(game)
        add_to_rss(game)
        tracking["added_ids"].append(game["id"])
        added_titles.append(game["title"])
        new_urls.append(f"{DOMAIN}/games/{game['slug']}.html")
        print(f"Added: {game['title']}")

    save_tracking(tracking)
    site_pages.build_home(site_shell.load_catalog())
    git_commit_and_push(added_titles)
    ping_indexnow(new_urls + [f"{DOMAIN}/"])


if __name__ == "__main__":
    main()
