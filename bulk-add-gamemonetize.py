#!/usr/bin/env python3
"""
Pixelsprout ONE-TIME bulk add for GameMonetize.

Sibling to bulk-add-games.py (GamePix) - same purpose (give the site a
broader starting GameMonetize catalog in one run), same page template,
same touchpoints. Shares gamemonetize-data.json with the daily
auto-add-gamemonetize.py script, so the two never add the same game
twice, exactly like bulk-add-games.py / auto-add-games.py already do
for GamePix.

Two real differences from the GamePix bulk script, both worth knowing:

1. NO QUALITY_SCORE FIELD. GamePix's feed includes a `quality_score` the
   bulk script filters on (MIN_QUALITY = 0.55). GameMonetize's feed has
   no equivalent field at all - checked directly against the real feed.
   This script uses minimum description length as a rough proxy instead.
   Be honest with yourself about what this catches: it filters out
   completely empty/one-line entries, not genuinely low-quality ones with
   a merely adequate description. It's a real filter, just a weaker one
   than GamePix's actual quality score.

2. DEFAULT CAP, not "no cap." The reference bulk-add-games.py has
   MAX_TOTAL = None (pulls everything that passes quality filter). Given
   GameMonetize's catalog is enormous (the company/publisher dropdown
   alone lists 1000+ entries) and every new game adds to the content
   engine's AI-guide backlog, this script defaults to a real cap
   (500) rather than "everything" - override with --max-total if you
   genuinely want more in one run.

Cross-catalog dedup works identically to auto-add-gamemonetize.py: every
candidate is checked against the ENTIRE existing catalog (any source)
using the same category+title-token scoring the content engine uses for
internal linking. This is a real, useful safety net - not a guarantee.
It reliably catches same-category near-duplicates; it can occasionally
miss cross-category ones that only share a single title word.
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
import similar_games as sim

RSS_FILE = "rss.xml"
RSS_MAX_ITEMS = 60

# ---- CONFIG ----
FEED_URL_TEMPLATE = "https://gamemonetize.com/feed.php?format=0&page={page}"
MAX_TOTAL_DEFAULT = 500          # see docstring point 2 - a real cap, not "everything"
MIN_DESCRIPTION_LENGTH = 80      # see docstring point 1 - weak proxy for quality, not a real score
MAX_PAGES_TO_CHECK_DEFAULT = 100 # safety ceiling to prevent a runaway loop, not a business limit
DUPLICATE_SCORE_THRESHOLD = 13   # same as auto-add-gamemonetize.py - kept identical on purpose
SITE_ROOT = "."
TRACKING_FILE = f"{SITE_ROOT}/gamemonetize-data.json"   # SAME file the daily script uses - this is what prevents double-adds
GAMES_INDEX_FILE = f"{SITE_ROOT}/games-index.json"
SITEMAP_FILE = f"{SITE_ROOT}/sitemap.xml"
GAMES_DIR = f"{SITE_ROOT}/games"
DOMAIN = "https://playpixelsprout.com"


# Identical to auto-add-gamemonetize.py's template - a bulk-added game
# page is indistinguishable from a daily-added one.


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


def fetch_bulk_games(already_added_ids, already_skipped_ids, existing_catalog, max_total, max_pages, min_desc_len):
    """
    Pulls games from the GameMonetize feed until max_total is reached or
    the feed/page ceiling runs out. Dedup happens against BOTH the
    existing site catalog (any source) AND against every game already
    picked earlier in this same run (a title could otherwise appear
    twice across different feed pages).
    """
    picked = []
    picked_this_run = []  # kept separate from existing_catalog so we can dedup against it too, cheaply
    per_category_count = {}
    page = 1

    while page <= max_pages and len(picked) < max_total:
        url = FEED_URL_TEMPLATE.format(page=page)
        try:
            with urllib.request.urlopen(url, timeout=20) as resp:
                items = json.loads(resp.read().decode())
        except Exception as e:
            print(f"  Feed page {page} fetch failed ({e}), stopping pagination.")
            break

        if not items:
            print(f"  Feed page {page} returned no items - reached the end of the catalog.")
            break

        for item in items:
            if len(picked) >= max_total:
                break

            raw_id = item.get("id")
            if not raw_id:
                continue
            gid = f"gm-{raw_id}"
            if gid in already_added_ids or gid in already_skipped_ids:
                continue

            title = (item.get("title") or "Untitled Game").strip()
            description = (item.get("description") or "").strip()
            category = (item.get("category") or "Arcade").strip().title()

            if len(description) < min_desc_len:
                continue  # weak quality proxy - see module docstring

            is_dup, matched_title = is_likely_duplicate(title, category, existing_catalog + picked_this_run)
            if is_dup:
                already_skipped_ids.add(gid)
                continue

            game = {
                "id": gid,
                "title": title,
                "category": category,
                "description": description,
                "thumbnail": item.get("thumb", ""),
                "embed_url": item.get("url", ""),
            }
            picked.append(game)
            picked_this_run.append({"title": title, "category": category})
            per_category_count[category] = per_category_count.get(category, 0) + 1

        page += 1

    return picked, per_category_count


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


def git_commit_and_push(added_titles):
    if not added_titles:
        print("No new games added — nothing to commit.")
        return
    subprocess.run(["git", "add", "."], check=True)
    msg = f"One-time bulk add: {len(added_titles)} GameMonetize games across categories"
    subprocess.run(["git", "commit", "-m", msg], check=True)
    subprocess.run(["git", "push"], check=True)
    print(f"Pushed: {msg}")


def main():
    parser = argparse.ArgumentParser(description="One-time bulk import from GameMonetize, deduped against the existing catalog.")
    parser.add_argument("--max-total", type=int, default=MAX_TOTAL_DEFAULT,
                         help=f"Cap on how many games to add this run (default: {MAX_TOTAL_DEFAULT}).")
    parser.add_argument("--max-pages", type=int, default=MAX_PAGES_TO_CHECK_DEFAULT)
    parser.add_argument("--min-description-length", type=int, default=MIN_DESCRIPTION_LENGTH,
                         help="Weak quality proxy - GameMonetize's feed has no real quality score.")
    args = parser.parse_args()

    tracking = load_tracking()
    already_added = set(tracking["added_ids"])
    already_skipped = set(tracking.get("skipped_duplicate_ids", []))
    existing_catalog = load_existing_catalog()

    print(f"Existing catalog: {len(existing_catalog)} games.")
    print(f"Fetching up to {args.max_total} new, non-duplicate GameMonetize games...")

    games, by_category = fetch_bulk_games(
        already_added, already_skipped, existing_catalog,
        args.max_total, args.max_pages, args.min_description_length,
    )

    tracking["skipped_duplicate_ids"] = list(already_skipped)

    if not games:
        print("No qualifying new games found.")
        save_tracking(tracking)
        return

    print(f"\nFound {len(games)} games to add:")
    for cat, count in sorted(by_category.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

    added_titles = []
    for game in games:
        game["slug"] = slugify(game["title"])
        build_game_page(game)
        add_to_sitemap(game)
        add_to_rss(game)
        tracking["added_ids"].append(game["id"])
        added_titles.append(game["title"])

    save_tracking(tracking)
    site_pages.build_home(site_shell.load_catalog())
    git_commit_and_push(added_titles)
    print(f"\nDone. Added {len(added_titles)} games.")


if __name__ == "__main__":
    main()
