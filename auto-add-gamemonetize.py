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
INDEX_FILE = f"{SITE_ROOT}/index.html"
SITEMAP_FILE = f"{SITE_ROOT}/sitemap.xml"
GAMES_DIR = f"{SITE_ROOT}/games"
DOMAIN = "https://playpixelsprout.com"

CATEGORY_COLORS = ["gold", "teal", "signal"]

# Identical template to auto-add-games.py, byte-for-byte, so a GameMonetize
# page is visually and structurally indistinguishable from a GamePix one.
GAME_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" type="image/png" href="../assets/logo-icon.png">
<title>{title} — Pixelsprout</title>
<meta name="description" content="Play {title} free online, no download needed.">
<link rel="stylesheet" href="../styles.css">
<link rel="preconnect" href="https://img.gamepix.com">
<link rel="preconnect" href="https://img.gamemonetize.com">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<script defer src="/_vercel/insights/script.js"></script>
<style>
  .embed-frame-wrap {{
    width: 100%;
    max-width: 480px;
    aspect-ratio: 480 / 320;
    border-radius: 8px;
    overflow: hidden;
    background: #000;
  }}
  .embed-frame-wrap iframe {{
    width: 100%;
    height: 100%;
    border: 0;
    display: block;
  }}
</style>
<script type="application/ld+json">{schema_json}</script>
<script type="application/ld+json">{breadcrumb_schema_json}</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-VTNJRV4WG8"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-VTNJRV4WG8');
</script>
</head>
<body>
<div class="game-shell" data-thumbnail="{thumbnail}">
  <div class="breadcrumb" style="font-family:'IBM Plex Mono',monospace;font-size:12px;color:var(--muted);margin-bottom:8px;">
    <a href="../index.html" style="color:var(--teal);text-decoration:none;">Home</a> / {category} / {title}
  </div>
  <a class="back-link" href="../index.html">← back to Pixelsprout</a>
  <h1 class="game-title">{title}</h1>
  <div class="game-meta">{category}</div>

  <div class="ad-slot ad-slot-banner">
    <ins class="adsbygoogle"
         style="display:block"
         data-ad-client="ca-pub-8466016918717424"
         data-ad-slot="4936643192"
         data-ad-format="auto"
         data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
  </div>

  <div class="game-board-frame">
    <div class="embed-frame-wrap">
      <iframe src="{embed_url}" allow="fullscreen; autoplay; screen-orientation;" scrolling="no" allowfullscreen title="{title}"></iframe>
    </div>
    <button class="action fullscreen-btn" onclick="
      const f = document.querySelector('.embed-frame-wrap');
      const req = f.requestFullscreen || f.webkitRequestFullscreen || f.msRequestFullscreen;
      if (req) req.call(f);
      if (typeof gtag === 'function') {{ gtag('event', 'fullscreen_click', {{ game_title: document.title }}); }}
    ">⛶ Fullscreen</button>
    <p class="how-to">{description}</p>

    <div class="ad-slot ad-slot-ribbon">
      <ins class="adsbygoogle"
           style="display:block"
           data-ad-client="ca-pub-8466016918717424"
           data-ad-slot="1457517471"
           data-ad-format="auto"
           data-full-width-responsive="true"></ins>
      <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
    </div>

    <div class="similar-games">
      <h3 class="similar-games-title">You might also like</h3>
      <div class="similar-games-grid" id="similar-games-grid"></div>
    </div>
    <script>
      fetch('../games-index.json')
        .then(r => r.json())
        .then(games => {{
          const currentSlug = '{slug}';
          const currentCategory = '{category}';
          let matches = games.filter(g => g.category === currentCategory && g.slug !== currentSlug);
          matches = matches.sort(() => 0.5 - Math.random());
          if (matches.length < 4) {{
            const others = games.filter(g => g.slug !== currentSlug && !matches.some(m => m.slug === g.slug));
            matches = matches.concat(others.sort(() => 0.5 - Math.random()).slice(0, 4 - matches.length));
          }}
          matches = matches.slice(0, 4);
          const grid = document.getElementById('similar-games-grid');
          matches.forEach(g => {{
            const a = document.createElement('a');
            a.className = 'similar-card';
            a.href = g.slug + '.html';
            a.innerHTML = '<img src="' + g.thumbnail + '" alt="" loading="lazy"><span>' + g.title + '</span>';
            grid.appendChild(a);
          }});
        }})
        .catch(() => {{}});
    </script>
  </div>
</div>
</body>
</html>
"""


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
    schema = {
        "@context": "https://schema.org",
        "@type": "VideoGame",
        "name": game["title"],
        "description": game["description"],
        "genre": game["category"],
        "url": f"https://playpixelsprout.com/games/{game['slug']}.html",
        "applicationCategory": "Game",
        "operatingSystem": "Web Browser",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
    }
    if game.get("thumbnail"):
        schema["image"] = game["thumbnail"]
    schema_json = json.dumps(schema)

    breadcrumb_schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://playpixelsprout.com/"},
            {"@type": "ListItem", "position": 2, "name": game["category"], "item": f"https://playpixelsprout.com/games/{game['slug']}.html"},
            {"@type": "ListItem", "position": 3, "name": game["title"], "item": f"https://playpixelsprout.com/games/{game['slug']}.html"},
        ],
    }
    breadcrumb_schema_json = json.dumps(breadcrumb_schema)

    html = GAME_PAGE_TEMPLATE.format(
        title=game["title"],
        category=game["category"],
        embed_url=game["embed_url"],
        description=game["description"],
        slug=game["slug"],
        schema_json=schema_json,
        breadcrumb_schema_json=breadcrumb_schema_json,
        thumbnail=game.get("thumbnail", ""),
    )
    path = f"{GAMES_DIR}/{game['slug']}.html"
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    update_games_index(game)
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


def add_card_to_index(game):
    with open(INDEX_FILE, encoding="utf-8") as f:
        index_html = f.read()

    category_heading = f"<h2>{game['category']}</h2>"
    existing_category = category_heading in index_html

    if existing_category:
        # Look up the color via the category div's own id attribute
        # (a slugified version of the category name) - simpler and more
        # exact than trying to pattern-match the surrounding structure.
        section_pattern = re.compile(
            r'<div id="' + re.escape(slugify(game["category"])) + r'" class="category (\w+)"'
        )
        section_match = section_pattern.search(index_html)
        game["color"] = section_match.group(1) if section_match else CATEGORY_COLORS[0]
    else:
        used_colors = re.findall(r'class="category (\w+)"', index_html)
        game["color"] = CATEGORY_COLORS[len(set(used_colors)) % len(CATEGORY_COLORS)]

    short_desc = game["description"][:70] + ("..." if len(game["description"]) > 70 else "")
    card_html = f'''    <a class="card" href="games/{game['slug']}.html" data-name="{game['title'].lower()}">
      <span class="icon-tile {game['color']}" style="padding:0; overflow:hidden;">
        <img src="{game['thumbnail']}" alt="" loading="lazy" style="width:100%; height:100%; object-fit:cover; border-radius:9px;">
      </span>
      <div class="card-body">
        <h3>{game['title']}</h3>
        <p>{short_desc}</p>
      </div>
    </a>
'''

    if existing_category:
        # Bump the displayed count for this category.
        count_pattern = re.compile(
            r'(' + re.escape(category_heading) + r'.*?<span class="count">)(\d+)( games?)(</span>)',
            re.DOTALL,
        )

        def _bump_count(m):
            new_count = int(m.group(2)) + 1
            plural = " games" if new_count != 1 else " game"
            return m.group(1) + str(new_count) + plural + m.group(4)

        index_html = count_pattern.sub(_bump_count, index_html, count=1)

        # Append the new card at the END of this category's grid, not the
        # start - keeps existing games ahead of newly-added ones in display
        # order (the order they were actually added to the site), instead
        # of every new addition jumping to the front and pushing everything
        # else down.
        grid_start_pattern = re.compile(
            re.escape(category_heading) + r'.*?<div class="grid" data-grid>\r?\n',
            re.DOTALL,
        )
        start_match = grid_start_pattern.search(index_html)
        if start_match:
            grid_content_start = start_match.end()
            end_match = re.search(
                r'\r?\n  <div id="[a-z0-9-]*" class="category |\r?\n  <p id="no-results"',
                index_html[grid_content_start:],
            )
            grid_content_end = (
                grid_content_start + end_match.start() if end_match else len(index_html)
            )
            index_html = (
                index_html[:grid_content_end]
                + card_html
                + index_html[grid_content_end:]
            )
    else:
        category_slug = slugify(game['category'])
        new_section = f'''  <div id="{category_slug}" class="category {game['color']}" data-section data-genre="{category_slug}">
    <span class="bar"></span>
    <h2>{game['category']}</h2>
    <span class="count">1 game</span>
  </div>
  <div class="grid" data-grid>
{card_html}  </div>

'''
        marker = '  <p id="no-results"'
        index_html = index_html.replace(marker, new_section + marker, 1)

    total_match = re.search(r'<strong id="game-count">(\d+)</strong>', index_html)
    if total_match:
        new_total = int(total_match.group(1)) + 1
        index_html = index_html.replace(
            f'<strong id="game-count">{total_match.group(1)}</strong>',
            f'<strong id="game-count">{new_total}</strong>',
            1,
        )

    marquee_match = re.search(r"const names = \[(.*?)\];", index_html)
    if marquee_match:
        new_names = marquee_match.group(1) + f",'{game['title'].upper()}'"
        index_html = index_html.replace(marquee_match.group(0), f"const names = [{new_names}];", 1)

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(index_html)


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
        add_card_to_index(game)
        add_to_sitemap(game)
        add_to_rss(game)
        tracking["added_ids"].append(game["id"])
        added_titles.append(game["title"])
        new_urls.append(f"{DOMAIN}/games/{game['slug']}.html")
        print(f"Added: {game['title']} ({game['category']})")

    save_tracking(tracking)
    git_commit_and_push(added_titles)
    ping_indexnow(new_urls + [f"{DOMAIN}/"])


if __name__ == "__main__":
    main()
