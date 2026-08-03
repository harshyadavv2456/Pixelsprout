"""
Deterministic game-similarity matching - no AI involved, so it's free,
fast, and 100% reproducible. Used to:
  1. pick the games a "games like X" page recommends
  2. pick the cross-links between a game's own guide pages
  3. pick the internal links shown inside AI-generated guide text

Similarity = same category (heavy weight) + shared significant title
words (light weight). Intentionally simple - this only needs to be
"reasonable," not perfect; the AI-written editorial text around the list
is what actually makes each page useful to read.
"""

import re

STOPWORDS = {
    "the", "a", "an", "of", "and", "for", "in", "on", "to", "vs", "2", "3",
    "game", "online", "free", "play", "simulator", "puzzle", "master",
    "world", "adventure", "challenge", "pro", "deluxe", "hd", "3d", "2d",
}


def _title_tokens(title):
    words = re.findall(r"[a-z0-9]+", title.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def build_index(games):
    """games: list of {slug, title, category, thumbnail} dicts."""
    for g in games:
        g["_tokens"] = _title_tokens(g["title"])
    return games


def find_similar(target, games, limit=10, exclude_slugs=None):
    """
    Returns up to `limit` games most similar to `target`, best match
    first. `games` must already have gone through build_index().
    """
    exclude_slugs = exclude_slugs or set()
    exclude_slugs = exclude_slugs | {target["slug"]}

    scored = []
    for g in games:
        if g["slug"] in exclude_slugs:
            continue
        score = 0
        if g["category"] == target["category"]:
            score += 10
        shared = target.get("_tokens", set()) & g.get("_tokens", set())
        score += len(shared) * 3
        if score > 0:
            scored.append((score, g))

    scored.sort(key=lambda x: -x[0])
    return [g for _, g in scored[:limit]]


def find_by_keywords(games, category_keywords=None, title_keywords=None, limit=20):
    """
    Used by the curated "games like [famous title]" collection pages -
    e.g. category_keywords=["runner"], title_keywords=["run","subway","dash"]
    for a Subway Surfers-style collection.
    """
    category_keywords = [k.lower() for k in (category_keywords or [])]
    title_keywords = [k.lower() for k in (title_keywords or [])]

    matches = []
    for g in games:
        cat = g["category"].lower()
        title = g["title"].lower()
        cat_hit = any(k in cat for k in category_keywords) if category_keywords else False
        title_hit = any(k in title for k in title_keywords) if title_keywords else False
        if cat_hit or title_hit:
            score = (2 if cat_hit else 0) + (3 if title_hit else 0)
            matches.append((score, g))

    matches.sort(key=lambda x: -x[0])
    return [g for _, g in matches[:limit]]
