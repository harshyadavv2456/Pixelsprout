#!/usr/bin/env python3
"""
Generates the 5 guide pages for each game that doesn't have them yet:
  /guides/<slug>-tips/
  /guides/<slug>-controls/
  /guides/<slug>-beginner-guide/
  /guides/<slug>-faq/
  /guides/games-like-<slug>/

Incremental and idempotent - tracks progress in content-engine/manifest.json
and only processes games not already in it, so this is safe to run daily
via GitHub Actions (after new games are added) without redoing work or
burning API quota on games you already have pages for.

Usage:
  python content-engine/generate_guides.py                  # process up to BATCH_LIMIT new games
  python content-engine/generate_guides.py --limit 10        # override batch size
  python content-engine/generate_guides.py --dry-run         # use fallback content, no API calls at all
  python content-engine/generate_guides.py --retry-fallback  # re-process games that only got fallback content last time
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

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAMES_INDEX_PATH = os.path.join(REPO_ROOT, "games-index.json")
MANIFEST_PATH = os.path.join(os.path.dirname(__file__), "manifest.json")
GUIDES_INDEX_PATH = os.path.join(REPO_ROOT, "guides-index.json")
SITEMAP_PATH = os.path.join(REPO_ROOT, "sitemap.xml")

BATCH_LIMIT_DEFAULT = 40  # games per run - keep this modest, this runs daily


def load_json(path, default):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def build_prompts(page_type, game, related_titles):
    related_str = ", ".join(related_titles) if related_titles else "other similar games"
    common_system = (
        "You are writing genuinely useful, specific web content for a free browser games "
        "site. Never write generic filler. Be concrete about THIS game. Respond with ONLY "
        "a JSON object matching the exact schema requested - no markdown, no commentary."
    )
    if page_type == "tips":
        user = (
            f'Game: "{game["title"]}" (category: {game["category"]}). '
            f'Write JSON: {{"intro": "1-2 sentence intro", '
            f'"tips": ["5-8 specific, actionable tips or strategies for this game"], '
            f'"conclusion": "1 sentence wrap-up"}}. '
            f"Base tips on what a game in this genre/category typically involves - "
            f"be specific and practical, not generic advice that could apply to any game."
        )
    elif page_type == "controls":
        user = (
            f'Game: "{game["title"]}" (category: {game["category"]}). This is a browser game '
            f'played with mouse/keyboard on desktop and touch on mobile. Write JSON: '
            f'{{"intro": "1 sentence", "desktop": "1-2 sentences on likely desktop controls for '
            f'a {game["category"]} game", "mobile": "1-2 sentences on likely touch controls", '
            f'"tips": ["2-3 short control-related tips"]}}.'
        )
    elif page_type == "beginner-guide":
        user = (
            f'Game: "{game["title"]}" (category: {game["category"]}). Write JSON: '
            f'{{"intro": "1-2 sentences", "what_it_is": "2-3 sentences describing what this '
            f'kind of game involves", "first_steps": ["3-5 concrete first steps for a new player"], '
            f'"who_its_for": "1 sentence on the target audience"}}.'
        )
    elif page_type == "similar":
        user = (
            f'Game: "{game["title"]}" (category: {game["category"]}). Similar games available: '
            f'{related_str}. Write JSON: {{"intro": "2-3 sentences introducing why someone who '
            f'likes {game["title"]} would enjoy these other {game["category"]} games, mentioning '
            f'the genre appeal generally (do not just list the game names back)."}}.'
        )
    elif page_type == "faq":
        user = (
            f'Game: "{game["title"]}" (category: {game["category"]}). Write JSON: '
            f'{{"faqs": [{{"question": "...", "answer": "..."}}, ...]}} with 5-8 question/answer '
            f'pairs a real player would search for about this specific game - free-to-play status, '
            f'mobile support, controls, difficulty, what makes it fun, common confusion points for '
            f'a {game["category"]} game. Answers should be 1-2 sentences, specific and useful.'
        )
    else:
        raise ValueError(page_type)
    return common_system, user


def get_content(client, page_type, game, related_titles, dry_run, stats):
    if not dry_run and client.has_keys:
        system, user = build_prompts(page_type, game, related_titles)
        result = client.generate_json(system, user)
        if result:
            stats["ai"] += 1
            return result, False
        stats["fallback_after_fail"] += 1
    stats["fallback"] += 1
    fallback_map = {
        "tips": fb.fallback_tips,
        "controls": fb.fallback_controls,
        "beginner-guide": fb.fallback_beginner_guide,
        "similar": fb.fallback_similar_intro,
        "faq": fb.fallback_faq,
    }
    return fallback_map[page_type](game), True


GUIDE_PAGE_TYPES = ["tips", "controls", "beginner-guide", "similar", "faq"]


def category_url_for(game):
    """
    Only returns a category page URL if that folder genuinely exists on
    the site - most of the 100+ distinct category values in games-index.json
    don't have a matching curated category page, and a broken internal
    link is worse than no link at all.
    """
    slug = game["category"].lower().replace(" ", "-")
    if os.path.isdir(os.path.join(REPO_ROOT, slug)):
        return f"/{slug}/"
    return None


def process_game(client, game, all_games, dry_run, stats):
    related = sim.find_similar(game, all_games, limit=8)
    related_titles = [g["title"] for g in related]
    category_url = category_url_for(game)

    page_urls = {}
    page_contents = {}
    for page_type in GUIDE_PAGE_TYPES:
        content, is_fallback = get_content(client, page_type, game, related_titles, dry_run, stats)
        page_contents[page_type] = (content, is_fallback)
        slug_suffix = {
            "tips": f"{game['slug']}-tips",
            "controls": f"{game['slug']}-controls",
            "beginner-guide": f"{game['slug']}-beginner-guide",
            "similar": f"games-like-{game['slug']}",
            "faq": f"{game['slug']}-faq",
        }[page_type]
        page_urls[page_type] = f"/guides/{slug_suffix}/"

    any_fallback = any(v[1] for v in page_contents.values())

    for page_type, (content, _) in page_contents.items():
        slug_suffix = page_urls[page_type].strip("/").split("/")[-1]
        out_dir = os.path.join(REPO_ROOT, "guides", slug_suffix)
        os.makedirs(out_dir, exist_ok=True)
        html = render.render_guide_page(page_type, game, content, related, page_urls, category_url)
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)

    return page_urls, any_fallback


def update_sitemap(new_urls):
    if not new_urls:
        return
    with open(SITEMAP_PATH, encoding="utf-8") as f:
        content = f.read()
    to_add = [u for u in new_urls if f"<loc>https://playpixelsprout.com{u}</loc>" not in content]
    if not to_add:
        return
    entries = "\n".join(f"  <url><loc>https://playpixelsprout.com{u}</loc><priority>0.5</priority></url>" for u in to_add)
    if "</urlset>" in content:
        content = content.replace("</urlset>", entries + "\n</urlset>")
    else:
        content = content + "\n" + entries
    with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=BATCH_LIMIT_DEFAULT)
    parser.add_argument("--dry-run", action="store_true", help="Use fallback content only, no API calls")
    parser.add_argument("--retry-fallback", action="store_true", help="Reprocess games that only got fallback content")
    args = parser.parse_args()

    all_games = load_json(GAMES_INDEX_PATH, [])
    if not all_games:
        print("games-index.json not found or empty - nothing to do.")
        return

    sim.build_index(all_games)
    manifest = load_json(MANIFEST_PATH, {})
    guides_index = load_json(GUIDES_INDEX_PATH, {})

    client = GroqRotatingClient()
    if not args.dry_run and not client.has_keys:
        print("No GROQ_API_KEY_1..5 found in environment - running in fallback mode.")
        print("(This still produces valid, structurally complete pages - just not AI-written.)")

    targets = []
    for g in all_games:
        entry = manifest.get(g["slug"])
        if entry is None:
            targets.append(g)
        elif args.retry_fallback and entry.get("any_fallback"):
            targets.append(g)
        if len(targets) >= args.limit:
            break

    if not targets:
        print("No new games to process. Everything in games-index.json already has guide pages.")
        return

    print(f"Processing {len(targets)} games...")
    stats = {"ai": 0, "fallback": 0, "fallback_after_fail": 0}
    new_sitemap_urls = []

    for i, game in enumerate(targets):
        print(f"[{i+1}/{len(targets)}] {game['title']} ({game['slug']})")
        page_urls, any_fallback = process_game(client, game, all_games, args.dry_run, stats)

        manifest[game["slug"]] = {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "any_fallback": any_fallback,
            "pages": page_urls,
        }
        guides_index[game["slug"]] = page_urls
        for url in page_urls.values():
            new_sitemap_urls.append(url)

        # Be polite to Groq's rate limits between games.
        if not args.dry_run and client.has_keys:
            time.sleep(1.5)

    save_json(MANIFEST_PATH, manifest)
    save_json(GUIDES_INDEX_PATH, guides_index)
    update_sitemap(new_sitemap_urls)

    print(f"\nDone. AI-generated pages: {stats['ai']}, fallback pages: {stats['fallback'] + stats['fallback_after_fail']}")
    print(f"Games processed this run: {len(targets)}. Remaining un-processed games: "
          f"{sum(1 for g in all_games if g['slug'] not in manifest)}")


if __name__ == "__main__":
    main()
