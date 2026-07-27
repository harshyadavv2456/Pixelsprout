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

# ---- CONFIG — fill in FEED_URL before first run ----
FEED_URL = "https://feeds.gamepix.com/v2/json?sid=P7924&pagination=12&page=1"
GAMES_PER_RUN = 3
MAX_PAGES_TO_CHECK = 5
SITE_ROOT = "."
TRACKING_FILE = f"{SITE_ROOT}/games-data.json"
INDEX_FILE = f"{SITE_ROOT}/index.html"
SITEMAP_FILE = f"{SITE_ROOT}/sitemap.xml"
GAMES_DIR = f"{SITE_ROOT}/games"
DOMAIN = "https://playpixelsprout.com"

CATEGORY_COLORS = ["gold", "teal", "signal"]

GAME_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" type="image/png" href="../assets/logo-icon.png">
<title>{title} — Pixelsprout</title>
<meta name="description" content="Play {title} free online, no download needed.">
<link rel="stylesheet" href="../styles.css">
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
  .source-note {{
    margin-top: 4px;
    font-size: 11px;
    color: var(--muted);
    font-family: 'IBM Plex Mono', monospace;
  }}
</style>
</head>
<body>
<div class="game-shell">
  <a class="back-link" href="../index.html">← back to Pixelsprout</a>
  <h1 class="game-title">{title}</h1>
  <div class="game-meta">{category}</div>

  <div class="game-board-frame">
    <div class="embed-frame-wrap">
      <iframe src="{embed_url}" allow="fullscreen; autoplay; screen-orientation;" scrolling="no" allowfullscreen title="{title}"></iframe>
    </div>
    <button class="action fullscreen-btn" onclick="
      const f = document.querySelector('.embed-frame-wrap');
      const req = f.requestFullscreen || f.webkitRequestFullscreen || f.msRequestFullscreen;
      if (req) req.call(f);
      if (screen.orientation && screen.orientation.lock) {{
        screen.orientation.lock('landscape').catch(() => {{}});
      }}
    ">⛶ Fullscreen</button>
    <p class="how-to">{description}</p>

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
            })
            if len(found) >= games_per_run:
                break

        url = data.get("next_url")
        pages_checked += 1

    return found


def build_game_page(game):
    html = GAME_PAGE_TEMPLATE.format(
        title=game["title"],
        category=game["category"],
        embed_url=game["embed_url"],
        description=game["description"],
        slug=game["slug"],
    )
    path = f"{GAMES_DIR}/{game['slug']}.html"
    with open(path, "w", encoding='utf-8') as f:
        f.write(html)
    update_games_index(game)
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


def add_card_to_index(game):
    with open(INDEX_FILE, encoding='utf-8') as f:
        index_html = f.read()

    category_heading = f"<h2>{game['category']}</h2>"
    existing_category = category_heading in index_html

    if existing_category:
        # Look up the color already used by this category's section, so the
        # new card matches the section it's being dropped into.
        section_pattern = re.compile(
            r'<div class="category (\w+)" data-section>\s*<span class="bar"></span>\s*'
            + re.escape(category_heading)
        )
        section_match = section_pattern.search(index_html)
        game["color"] = section_match.group(1) if section_match else CATEGORY_COLORS[0]
    else:
        used_colors = re.findall(r'class="category (\w+)"', index_html)
        game["color"] = CATEGORY_COLORS[len(set(used_colors)) % len(CATEGORY_COLORS)]

    short_desc = game['description'][:70] + ('...' if len(game['description']) > 70 else '')
    card_html = f'''    <a class="card" href="games/{game['slug']}.html" data-name="{game['title'].lower()}">
      <span class="icon-tile {game['color']}" style="padding:0; overflow:hidden;">
        <img src="{game['thumbnail']}" alt="" style="width:100%; height:100%; object-fit:cover; border-radius:9px;">
      </span>
      <div class="card-body">
        <h3>{game['title']}</h3>
        <p>{short_desc}</p>
      </div>
    </a>
'''

    if existing_category:
        # Insert the card right after this category's <div class="grid" data-grid>
        # opening tag, and bump its displayed count by 1.
        grid_pattern = re.compile(
            re.escape(category_heading) + r'.*?<span class="count">(\d+)( games?)</span>.*?<div class="grid" data-grid>\n',
            re.DOTALL,
        )
        match = grid_pattern.search(index_html)
        if match:
            new_count = int(match.group(1)) + 1
            plural = " games" if new_count != 1 else " game"
            block = match.group(0)
            block = block.replace(f'{match.group(1)}{match.group(2)}</span>', f'{new_count}{plural}</span>', 1)
            index_html = (
                index_html[:match.start()]
                + block
                + card_html
                + index_html[match.end():]
            )
    else:
        new_section = f'''  <div class="category {game['color']}" data-section>
    <span class="bar"></span>
    <h2>{game['category']}</h2>
    <span class="count">1 game</span>
  </div>
  <div class="grid" data-grid>
{card_html}  </div>

'''
        marker = '  <p id="no-results"'
        index_html = index_html.replace(marker, new_section + marker, 1)

    # Bump total games-live count
    total_match = re.search(r'<strong id="game-count">(\d+)</strong>', index_html)
    if total_match:
        new_total = int(total_match.group(1)) + 1
        index_html = index_html.replace(
            f'<strong id="game-count">{total_match.group(1)}</strong>',
            f'<strong id="game-count">{new_total}</strong>',
            1,
        )

    # Add to marquee ticker names array
    marquee_match = re.search(r"const names = \[(.*?)\];", index_html)
    if marquee_match:
        new_names = marquee_match.group(1) + f",'{game['title'].upper()}'"
        index_html = index_html.replace(marquee_match.group(0), f"const names = [{new_names}];", 1)

    with open(INDEX_FILE, "w", encoding='utf-8') as f:
        f.write(index_html)


def add_to_sitemap(game):
    with open(SITEMAP_FILE, encoding='utf-8') as f:
        sitemap = f.read()
    new_url = f'  <url><loc>{DOMAIN}/games/{game["slug"]}.html</loc><priority>0.7</priority></url>\n'
    sitemap = sitemap.replace("</urlset>", new_url + "</urlset>")
    with open(SITEMAP_FILE, "w", encoding='utf-8') as f:
        f.write(sitemap)


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
    for game in new_games:
        game["slug"] = slugify(game["title"])
        build_game_page(game)
        add_card_to_index(game)
        add_to_sitemap(game)
        tracking["added_ids"].append(game["id"])
        added_titles.append(game["title"])
        print(f"Added: {game['title']}")

    save_tracking(tracking)
    git_commit_and_push(added_titles)


if __name__ == "__main__":
    main()
