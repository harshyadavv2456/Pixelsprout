"""
Deterministic game-similarity matching - no AI involved, so it's free,
fast, and 100% reproducible. Used to:
  1. pick the games a "games like X" page recommends
  2. pick the cross-links between a game's own guide pages
  3. pick the internal links shown inside AI-generated guide text

Similarity = same category (heavy weight) + shared significant title
words (light weight). Game-page picks (pick_similar) additionally require the
same mechanic (derived from title/tags/description) when 4+ games share it. Intentionally simple - this only needs to be
"reasonable," not perfect; the AI-written editorial text around the list
is what actually makes each page useful to read.
"""

import json
import os
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


# Hand-picked lists that replace the automatic match for specific games,
# used when category/title matching gives poor results. Approved by Studio.
CURATED_SIMILAR = {
    # Getting Over It is listed as Strategy, so the automatic match pulled in
    # tower defense and management games. These are precision/physics climbers.
    "getting-over-it": [
        "hammer-climb-miniscrafter",
        "mad-climbing",
        "bike-mania-2",
        "carrot-climber",
        "stickman-that-one-level",
    ],
    # The games named in the "games like Protect My Dog" guide: draw-a-line rescue puzzles.
    "protect-my-dog": [
        "save-the-doge",
        "draw-save-puzzle",
        "stickman-rescue-draw-2-save",
        "draw-2-save-stickman-puzzle",
        "protect-the-thief",
    ],
    # The automatic match pulled in unrelated Skill games. These are drop-and-stack timing games.
    "books-tower": [
        "tower-blocks-deluxe-3d",
        "stack-block-up",
        "color-tower-2-drop-the-boxes-3d",
        "buildtower",
    ],
}


def _excluded_slugs():
    """excluded-games.json at the repo root (see site_shell.load_excluded_slugs)."""
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "excluded-games.json")
    try:
        with open(path, encoding="utf-8") as f:
            return {g["slug"] if isinstance(g, dict) else g for g in json.load(f).get("games", [])}
    except (OSError, ValueError):
        return set()


EXCLUDED_SLUGS = _excluded_slugs()


# ---------------------------------------------------------------------------
# Mechanic-aware picks (the "Games like this" rail/shelf on game pages)
# ---------------------------------------------------------------------------
# A game's mechanic is derived from its title, tags and description keywords.
# First matching rule wins, so more specific rules come first. Patterns are
# matched against lower-cased text. Single-word patterns (no space/hyphen in
# them) are only trusted on the title/tags/slug; descriptions need a phrase, so a
# blurb like "clear lines" doesn't make a block game a line-drawing game.
MECHANIC_RULES = [
    ("connect-dots", [r"connect(?:ing)?[ -]the[ -]dots?", r"connect[ -]dots?", r"dot[ -]?link",
                      r"link[ -]the[ -]dots?", r"dots?[ -]connect", r"draw[ -](?:the[ -])?(?:line|path)s?",
                      r"line[ -]draw(?:ing)?", r"path[ -]draw(?:ing)?", r"one[ -]line", r"one[ -]stroke",
                      r"flow[ -]free", r"\bdots\b", r"\blinks?\b", r"\blines\b", r"line[ -](?:puzzle|creator)", r"emoji[ -]line", r"\bflow\b", r"path"]),
    ("bubble-shooter", [r"bubble[ -]?shoot", r"bubble[ -]pop", r"puzzle[ -]?bubble", r"\bbubbles?\b", r"^bubble(?!head)"]),
    ("sort", [r"water[ -]sort", r"ball[ -]sort", r"colou?r[ -]sort", r"\bsort(?:ing|er)?\b", r"test[ -]?tubes?"]),
    ("climb-rage", [r"getting[ -]over[ -]it", r"\bclimb(?:er|ing|s)?\b", r"\brage\b", r"only[ -]up",
                    r"jump[ -]king", r"that[ -]one[ -]level", r"\bhammer[ -]climb"]),
    ("2048-merge", [r"\b2048\b", r"\bmerge\b", r"\bmerging\b"]),
]
_MECHANIC_RES = [(name, [(re.compile(p), "[ -]" in p) for p in pats]) for name, pats in MECHANIC_RULES]
MIN_MECHANIC_MATCHES = 4
# Never a mechanic pick: titles that hit a keyword but aren't that kind of game
# (checked against their game-page descriptions). Approved by Studio.
MECHANIC_DENY = {
    "zombies-vs-lines",
    "paty-path",
    "princess-stripes-vs-dots",  # dress-up game
    "worms-lines",               # tile-painting maze, not line drawing
    "color-lines",               # ball-matching game, not line drawing
}
_GAMES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "games")
_DESC_RE = re.compile(r'<meta name="description" content="([^"]*)"')
_KEYWORDS_RE = re.compile(r'<meta name="keywords" content="([^"]*)"')
_NOINDEX_RE = re.compile(r'<meta name="robots" content="[^"]*noindex')
_page_cache = {}


def _page_info(slug):
    """(description + keywords text, noindexed, broken) read from games/<slug>.html."""
    if slug not in _page_cache:
        path = os.path.join(_GAMES_DIR, f"{slug}.html")
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                doc = f.read()
        except OSError:
            _page_cache[slug] = ("", False, True)  # no game page = broken link
            return _page_cache[slug]
        text = " ".join(m.group(1) for r in (_DESC_RE, _KEYWORDS_RE) for m in [r.search(doc)] if m)
        # The stock description ("Play X free online, no download needed.") adds nothing.
        text = re.sub(r"free online|no download needed|instant browser play", " ", text.lower())
        _page_cache[slug] = (text, bool(_NOINDEX_RE.search(doc)), False)
    return _page_cache[slug]


def mechanic_of(game):
    """Mechanic key for a game, or None. Title and tags are checked before the description."""
    if game.get("slug") in MECHANIC_DENY:
        return None
    tags = game.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]
    strong = " ".join([game.get("title") or "", " ".join(tags), game.get("slug", "").replace("-", " ")]).lower()
    weak = " ".join([game.get("description") or "", _page_info(game["slug"])[0]]).lower()
    for text, phrases_only in ((strong, False), (weak, True)):
        for name, regexes in _MECHANIC_RES:
            if any(r.search(text) for r, is_phrase in regexes if is_phrase or not phrases_only):
                return name
    return None


def _usable(g, exclude):
    if g["slug"] in exclude or g["slug"] in EXCLUDED_SLUGS:
        return False
    _, noindexed, broken = _page_info(g["slug"])
    return not noindexed and not broken


def pick_similar(slug, category, catalog, count=18, primary_category=None, stable_hash=None):
    """
    Game-page "Games like this" picks. Order:
      1. CURATED_SIMILAR override, if any.
      2. Same primary category AND same mechanic, then the same mechanic filed
         under another category (e.g. bubble shooters listed as Arcade).
      3. Only if fewer than MIN_MECHANIC_MATCHES games matched in step 2:
         same-category fill, then any-category fill (the old behaviour).
    Excluded (excluded-games.json), noindexed and broken games are never picked.
    """
    primary_category = primary_category or (lambda c: c)
    import hashlib
    stable_hash = stable_hash or (lambda v: int(hashlib.md5(v.encode("utf-8")).hexdigest(), 16))
    exclude = {slug}
    by_slug = {g["slug"]: g for g in catalog}
    curated = CURATED_SIMILAR.get(slug)
    if curated:
        return [by_slug[s] for s in curated if s in by_slug and _usable(by_slug[s], exclude)][:count]

    target = by_slug.get(slug) or {"slug": slug, "title": slug.replace("-", " "), "category": category}
    mech = mechanic_of(target)
    primary = primary_category(category)
    same = [g for g in catalog if primary_category(g.get("category", "")) == primary and _usable(g, exclude)]

    def order(g, salt=""):
        return (not g.get("thumbnail"), stable_hash(slug + salt + g["slug"]))

    picks = []
    if mech:
        same_slugs = {g["slug"] for g in same}
        picks = sorted((g for g in same if mechanic_of(g) == mech), key=order)
        picks += sorted((g for g in catalog if g["slug"] not in same_slugs and mechanic_of(g) == mech
                         and g.get("thumbnail") and _usable(g, exclude)), key=lambda g: order(g, "~m"))
        picks = picks[:count]
    if len(picks) >= MIN_MECHANIC_MATCHES:
        return picks
    taken = {g["slug"] for g in picks}
    picks += sorted((g for g in same if g["slug"] not in taken), key=order)[: count - len(picks)]
    if len(picks) < count:
        taken = {g["slug"] for g in picks}
        rest = [g for g in catalog if g["slug"] not in taken and g.get("thumbnail") and _usable(g, exclude)]
        rest.sort(key=lambda g: stable_hash(slug + "~" + g["slug"]))
        picks += rest[: count - len(picks)]
    return picks


def _primary_category():
    """site_shell.primary_category (category aliases), or identity if unavailable."""
    try:
        import sys
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if root not in sys.path:
            sys.path.insert(0, root)
        import site_shell
        return site_shell.primary_category
    except ImportError:
        return lambda c: c


def find_similar(target, games, limit=10, exclude_slugs=None):
    """
    Returns up to `limit` games most similar to `target`, best match first
    (guide cross-links). `games` must already have gone through build_index().
    Same rules as the game pages (pick_similar): hand-picked override first,
    then same category + same mechanic (then same mechanic elsewhere). Only
    when fewer than MIN_MECHANIC_MATCHES match does it fill with the original
    category + shared-title-word scoring. Deny-listed games never count as
    mechanic matches; excluded, noindexed and broken games are never picked.
    """
    exclude = set(exclude_slugs or ()) | {target["slug"]}
    usable = [g for g in games if _usable(g, exclude)]
    by_slug = {g["slug"]: g for g in usable}

    curated = CURATED_SIMILAR.get(target["slug"])
    if curated:
        return [by_slug[s] for s in curated if s in by_slug][:limit]

    primary = _primary_category()
    picks = []
    mech = mechanic_of(target)
    if mech:
        pc = primary(target.get("category", ""))
        same = [g for g in usable if primary(g.get("category", "")) == pc and mechanic_of(g) == mech]
        other = [g for g in usable if primary(g.get("category", "")) != pc and mechanic_of(g) == mech]
        picks = (same + other)[:limit]
    if len(picks) >= MIN_MECHANIC_MATCHES:
        return picks

    taken = {g["slug"] for g in picks}
    scored = []
    for g in usable:
        if g["slug"] in taken:
            continue
        score = 0
        if g["category"] == target["category"]:
            score += 10
        shared = target.get("_tokens", set()) & g.get("_tokens", set())
        score += len(shared) * 3
        if score > 0:
            scored.append((score, g))
    scored.sort(key=lambda x: -x[0])
    return picks + [g for _, g in scored[: limit - len(picks)]]


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
        if g["slug"] in EXCLUDED_SLUGS:
            continue
        cat = g["category"].lower()
        title = g["title"].lower()
        cat_hit = any(k in cat for k in category_keywords) if category_keywords else False
        title_hit = any(k in title for k in title_keywords) if title_keywords else False
        if cat_hit or title_hit:
            score = (2 if cat_hit else 0) + (3 if title_hit else 0)
            matches.append((score, g))

    matches.sort(key=lambda x: -x[0])
    return [g for _, g in matches[:limit]]
