#!/usr/bin/env python3
"""
Pixelsprout GameMonetize auto-add script.

Sibling to auto-add-games.py (GamePix) - same page template, same
touchpoints (games-index.json, sitemap.xml, rss.xml, IndexNow, homepage
card), same small-daily-batch philosophy. The one thing this one does
that the GamePix script doesn't need to: cross-catalog dedup, since
GameMonetize and GamePix license largely overlapping studio libraries.
Before adding any GameMonetize game, this checks it against every game
already in games-index.json (from ANY source) and skips it if something
too similar already exists.

Designed to run as an additional step in the same GitHub Actions job as
auto-add-games.py (see .github/workflows/auto-add-games.yml) - not a
separate scheduled workflow, so there's no risk of two jobs racing to
commit/push the same files.
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

sys.path.insert(0, "content-engine")
import similar_games as sim  # reuses the exact same title/category matching already used for internal linking

RSS_FILE = "rss.xml"
RSS_MAX_ITEMS = 60
INDEXNOW_KEY = "09266bfbb51ba867175e9483e9d5fa6d"

FEED_URL_TEMPLATE = "https://gamemonetize.com/feed.php?format=0&page={page}"
GAMES_PER_RUN = 3          # same daily pace as the GamePix importer - deliberate, not a limitation
MAX_PAGES_TO_CHECK = 20    # GameMonetize's catalog is huge; may need several pages to find non-duplicate games
DUPLICATE_SCORE_THRESHOLD = 13   # same category (10) + at least one shared title word (3) = skip as likely-duplicate
SITE_ROOT = "."
TRACKING_FILE = f"{SITE_ROOT}/gamemonetize-data.json"   # separate from games-data.json (GamePix) - avoids any ID collision risk
GAMES_INDEX_FILE = f"{SITE_ROOT}/games-index.json"
SITEMAP_FILE = f"{SITE_ROOT}/sitemap.xml"
GAMES_DIR = f"{SITE_ROOT}/games"
DOMAIN = "https://playpixelsprout.com"


# Identical template to auto-add-games.py, byte-for-byte, so a GameMonetize
# page is visually and structurally indistinguishable from a GamePix one.


def slugify(title):
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def load_tracking():
    try:
        with open(TRACKING_FILE, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"added_ids": [], "skipped_duplicate_ids": []}


def save_tracking(data):
    with open(TRACKING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_existing_catalog():
    try:
        with open(GAMES_INDEX_FILE, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def is_likely_duplicate(candidate_title, candidate_category, existing_catalog):
    """
    Checks a GameMonetize candidate against the WHOLE existing catalog
    (any source) using the same token-overlap scoring the content engine
    already uses for internal linking. Same category + at least one shared
    significant title word scores 13, which is our skip threshold - high
    enough to catch genuine near-duplicates (e.g. two "Wolfoo Maze"-style
    reskins) without being so aggressive it skips everything in a popular
    genre like Puzzle or Arcade.
    """
    cand_tokens = sim._title_tokens(candidate_title)
    for g in existing_catalog:
        score = 0
        if g.get("category", "").lower() == candidate_category.lower():
            score += 10
        shared = cand_tokens & sim._title_tokens(g["title"])
        score += len(shared) * 3
        if score >= DUPLICATE_SCORE_THRESHOLD:
            return True, g["title"]
    return False, None


def fetch_new_games(already_added_ids, already_skipped_ids, existing_catalog, games_per_run, max_pages):
    found = []
    page = 1

    while page <= max_pages and len(found) < games_per_run:
        url = FEED_URL_TEMPLATE.format(page=page)
        try:
            with urllib.request.urlopen(url, timeout=20) as resp:
                items = json.loads(resp.read().decode())
        except Exception as e:
            print(f"  Feed page {page} fetch failed ({e}), stopping pagination.")
            break

        if not items:
            break

        for item in items:
            raw_id = item.get("id")
            if not raw_id:
                continue
            gid = f"gm-{raw_id}"
            if gid in already_added_ids or gid in already_skipped_ids:
                continue

            title = (item.get("title") or "Untitled Game").strip()
            category = (item.get("category") or "Arcade").strip().title()

            is_dup, matched_title = is_likely_duplicate(title, category, existing_catalog)
            if is_dup:
                print(f"  SKIP (too similar to existing '{matched_title}'): {title}")
                already_skipped_ids.add(gid)
                continue

            found.append({
                "id": gid,
                "title": title,
                "category": category,
                "description": (item.get("description") or "").strip(),
                "thumbnail": item.get("thumb", ""),
                "embed_url": item.get("url", ""),
            })
            if len(found) >= games_per_run:
                break

        page += 1

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
    try:
        with open(GAMES_INDEX_FILE, encoding="utf-8") as f:
            games_list = json.load(f)
    except FileNotFoundError:
        games_list = []
    games_list.append({
        "slug": game["slug"],
        "title": game["title"],
        "category": game["category"],
        "thumbnail": game["thumbnail"],
        "source": "gamemonetize",
    })
    with open(GAMES_INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(games_list, f)



def add_to_sitemap(game):
    with open(SITEMAP_FILE, encoding="utf-8") as f:
        sitemap = f.read()
    new_url = f'  <url><loc>{DOMAIN}/games/{game["slug"]}.html</loc><priority>0.7</priority></url>\n'
    sitemap = sitemap.replace("</urlset>", new_url + "</urlset>")
    with open(SITEMAP_FILE, "w", encoding="utf-8") as f:
        f.write(sitemap)


def add_to_rss(game):
    try:
        with open(RSS_FILE, encoding="utf-8") as f:
            rss = f.read()
    except FileNotFoundError:
        print("rss.xml not found — skipping RSS update.")
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

    with open(RSS_FILE, "w", encoding="utf-8") as f:
        f.write(rss)


def ping_indexnow(urls):
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
        print("No new GameMonetize games added — nothing to commit.")
        return
    subprocess.run(["git", "add", "."], check=True)
    msg = "Auto-add GameMonetize games: " + ", ".join(added_titles)
    subprocess.run(["git", "commit", "-m", msg], check=True)
    subprocess.run(["git", "push"], check=True)
    print(f"Pushed: {msg}")


def main():
    parser = argparse.ArgumentParser(description="Add new games to Pixelsprout from the GameMonetize feed, deduped against the existing catalog.")
    parser.add_argument("--count", type=int, default=GAMES_PER_RUN)
    parser.add_argument("--max-pages", type=int, default=MAX_PAGES_TO_CHECK)
    args = parser.parse_args()

    tracking = load_tracking()
    already_added = set(tracking["added_ids"])
    already_skipped = set(tracking.get("skipped_duplicate_ids", []))
    existing_catalog = load_existing_catalog()
    print(f"Existing catalog: {len(existing_catalog)} games. Checking GameMonetize feed for {args.count} new, non-duplicate games...")

    new_games = fetch_new_games(already_added, already_skipped, existing_catalog, args.count, args.max_pages)

    tracking["skipped_duplicate_ids"] = list(already_skipped)

    if not new_games:
        print("No new non-duplicate games found this run.")
        save_tracking(tracking)
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
        print(f"Added: {game['title']} ({game['category']})")

    save_tracking(tracking)
    site_pages.build_home(site_shell.load_catalog())
    git_commit_and_push(added_titles)
    ping_indexnow(new_urls + [f"{DOMAIN}/"])


if __name__ == "__main__":
    main()
