"""Shared page shell for every generated Pixelsprout page.

Every generator (auto-add, bulk-add, category pages, homepage, guides,
collections, migrate-ui) renders through this module so the header, rail,
footer, cards and ad slots stay identical site-wide.
"""

import datetime
import hashlib
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
DOMAIN = "https://playpixelsprout.com"
ASSET_VERSION = "20260923"

ADSENSE_CLIENT = "ca-pub-8466016918717424"
AD_SLOT_BANNER = "4936643192"
AD_SLOT_RIBBON = "1457517471"
GA_ID = "G-VTNJRV4WG8"
ADSTERRA_RECT_KEY = "9de242ffc7b556a74ae29033348b18bd"
ADSTERRA_LEADER_KEY = "da5095b2daea5c6ba87d034975239610"
ADSTERRA_NATIVE_KEY = "c3f3d41bbefde3a25a4d5d341b5582d1"
ADSTERRA_NATIVE_SRC = f"https://pl30771855.effectivecpmnetwork.com/{ADSTERRA_NATIVE_KEY}/invoke.js"

FONTS_HREF = (
    "https://fonts.googleapis.com/css2?"
    "family=Bricolage+Grotesque:opsz,wght@12..96,500..700"
    "&family=Geist:wght@400..600"
    "&family=Geist+Mono:wght@400..500"
    "&display=swap"
)
WORDMARK_FONT_HREF = "https://fonts.googleapis.com/css2?family=Press+Start+2P&text=PIXELSPROUT&display=swap"

GAMES_INDEX = os.path.join(ROOT, "games-index.json")
FALLBACK_THUMB = "/assets/logo-icon.png"


def esc(value):
    return html.escape(str(value or ""), quote=True)


def text(value):
    """Plain text from an HTML fragment (entities decoded, tags dropped)."""
    return html.unescape(re.sub(r"<[^>]+>", "", value or "")).strip()


def slugify(value):
    return re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")


# ---------------------------------------------------------------------------
# Genres
# ---------------------------------------------------------------------------

# Feed-level duplicates that should read as one genre on the site.
CATEGORY_ALIASES = {
    "Hyper-Casual": "Hypercasual",
    "2 Player": "Two-Player",
    ".Io": "Io",
    "Games-For-Girls": "Girls",
    "Shooter": "Shooting",
}

PRETTY_NAMES = {
    "First-Person-Shooter": "First-Person Shooter",
    "Games-For-Girls": "Games for Girls",
    "Two-Player": "Two Player",
    "2 Player": "Two Player",
    "Hyper-Casual": "Hypercasual",
    "Match-3": "Match 3",
    "Io": ".io",
    ".Io": ".io",
    "3D": "3D",
    "2048": "2048",
    "Rpg": "RPG",
}

GENRE_ICONS = {
    "Puzzle": "g-puzzle", "Match-3": "g-puzzle", "Jigsaw-Puzzles": "g-puzzle", "2048": "g-brain",
    "Arcade": "g-arcade", "Retro": "g-arcade", "Classics": "g-arcade",
    "Action": "g-action", "Addictive": "g-action",
    "Adventure": "g-adventure", "Escape": "g-adventure",
    "Sports": "g-sports", "Soccer": "g-sports", "Basketball": "g-sports",
    "Racing": "g-racing", "Driving": "g-car", "Car": "g-car",
    "Kids": "g-kids", "Fun": "g-kids",
    "Casual": "g-casual", "Cooking": "g-casual",
    "Clicker": "g-clicker",
    "Shooting": "g-shooting", "Shooter": "g-shooting", "First-Person-Shooter": "g-shooting", "Tanks": "g-shooting",
    "Two-Player": "g-two", "Multiplayer": "g-multi", "Io": "g-multi",
    "Hypercasual": "g-hyper", "Hyper-Casual": "g-hyper", "Skill": "g-hyper",
    "Girls": "g-girls", "Games-For-Girls": "g-girls", "Boys": "g-kids",
    "Strategy": "g-strategy", "Platformer": "g-platformer", "Runner": "g-platformer", "Stickman": "g-platformer",
    "Fighting": "g-fighting", "Battle": "g-fighting", "Zombie": "g-fighting", "Monster": "g-fighting", "Horror": "g-fighting",
    "Board": "g-board", "Trivia": "g-brain", "Brain": "g-brain", "Math": "g-brain",
    "Animal": "g-animal", "Dinosaur": "g-animal",
    "Simulation": "layers", "Drawing": "g-default",
}

DOT_COLORS = ["#8BD46A", "#E3C46B", "#E58FA8", "#7FB6E6", "#B59CE6", "#6FD0C5", "#E89F6B", "#A7B0BE"]

RAIL_GENRES = [
    "Puzzle", "Arcade", "Action", "Adventure", "Sports", "Racing", "Kids", "Casual",
    "Clicker", "Shooting", "Two-Player", "Multiplayer", "Hypercasual", "Girls", "Strategy", "Platformer",
]

FOOTER_GENRES = ["Puzzle", "Arcade", "Action", "Adventure", "Sports", "Racing", "Kids", "Strategy"]


def primary_category(category):
    return CATEGORY_ALIASES.get(category, category)


def pretty_genre(category):
    category = category or ""
    if category in PRETTY_NAMES:
        return PRETTY_NAMES[category]
    words = re.split(r"[-\s]+", category)
    out = []
    for i, w in enumerate(words):
        if not w:
            continue
        if i and w.lower() in {"for", "and", "of", "the"}:
            out.append(w.lower())
        elif w.isupper() or w[0].isdigit():
            out.append(w)
        else:
            out.append(w[0].upper() + w[1:].lower())
    return " ".join(out) or "Games"


def genre_icon(category):
    return GENRE_ICONS.get(category) or GENRE_ICONS.get(primary_category(category)) or "g-default"


def genre_color(category):
    key = primary_category(category or "").lower()
    idx = int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16) % len(DOT_COLORS)
    return DOT_COLORS[idx]


_category_dirs = None


def category_dirs():
    global _category_dirs
    if _category_dirs is None:
        found = set()
        for name in os.listdir(ROOT):
            if name.startswith(".") or name in {"games", "assets", "guides", "games-like", "api",
                                                  "content-engine", "cold-read", "gift-file",
                                                  "all-games", "node_modules", "legacy-scripts",
                                                  "qa-screenshots", "qa"}:
                continue
            if os.path.isfile(os.path.join(ROOT, name, "index.html")):
                found.add(name)
        _category_dirs = found
    return _category_dirs


def reset_category_dirs():
    global _category_dirs
    _category_dirs = None


def category_url(category):
    """URL of the genre's landing page, or None when the site has no such page."""
    for candidate in (category, primary_category(category)):
        slug = slugify(candidate)
        if slug and slug in category_dirs():
            return f"/{slug}/"
    return None


# ---------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------

def load_catalog(path=GAMES_INDEX):
    try:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
    except FileNotFoundError:
        return []
    seen, games = set(), []
    for g in raw:
        slug = g.get("slug")
        if not slug or slug in seen:
            continue
        seen.add(slug)
        g["title"] = clean_title(g.get("title") or slug)
        games.append(g)
    return games


def clean_title(title):
    return re.sub(r"[​-‍﻿]", "", html.unescape(title)).strip()


def thumb_of(game, size=None):
    url = (game.get("thumbnail") or "").strip()
    if not url:
        return FALLBACK_THUMB
    if size and "img.gamepix.com" in url:
        url = re.sub(r"([?&])w=\d+", rf"\g<1>w={size}", url)
    return url


def stable_hash(value):
    return int(hashlib.md5(value.encode("utf-8")).hexdigest(), 16)


def source_rank(game):
    return 1 if game.get("source") == "gamemonetize" else 0


# ---------------------------------------------------------------------------
# Small components
# ---------------------------------------------------------------------------

def icon(name, cls="i"):
    return f'<svg class="{cls}" aria-hidden="true"><use href="/assets/icons.svg#{name}"></use></svg>'


def card(game, show_meta=True, index=None, extra_class="", newness=None):
    slug = game["slug"]
    title = game["title"]
    category = game.get("category", "")
    attrs = f' data-name="{esc(title.lower())}"'
    if index is not None:
        attrs += f' data-i="{index}"'
    if newness is not None:
        attrs += f' data-n="{newness}"'
    cls = "card" + (f" {extra_class}" if extra_class else "")
    meta = f'<span class="card__meta">{esc(pretty_genre(category))}</span>' if show_meta and category else ""
    return (
        f'<a class="{cls}" href="/games/{esc(slug)}.html"{attrs}>'
        f'<span class="card__media"><img src="{esc(thumb_of(game))}" alt="{esc(title)}" width="320" height="320" loading="lazy" decoding="async"></span>'
        f'<span class="card__title">{esc(title)}</span>{meta}</a>'
    )


def tool_card(href, title, subtitle, image):
    return (
        f'<a class="card card--tool" href="{href}" data-name="{esc(title.lower())}">'
        f'<span class="card__media"><img src="{image}" alt="{esc(title)}" width="320" height="320" loading="lazy" decoding="async"></span>'
        f'<span class="card__title">{esc(title)}</span><span class="card__meta">{esc(subtitle)}</span></a>'
    )


TOOL_CARDS = [
    ("/cold-read/", "Cold Read", "Pixelsprout original", "/assets/cold-read-logo.jpg"),
    ("/gift-file/", "Guess It Box", "Pixelsprout original", "/assets/gift-file-logo.jpg"),
]


def crumbs(items):
    """items: [(label_html, href_or_None)] - label is already HTML-safe."""
    parts = []
    last = len(items) - 1
    for i, (label, href) in enumerate(items):
        if href and i != last:
            parts.append(f'<a href="{esc(href)}">{label}</a>')
        else:
            parts.append(f'<span aria-current="page">{label}</span>')
    sep = '<span class="crumbs__sep" aria-hidden="true">/</span>'
    return f'<nav class="crumbs" aria-label="Breadcrumb">{sep.join(parts)}</nav>'


def shelf(title_html, cards_html, *, more_href=None, more_label="See all", count=None,
          dot=None, section_id=None, extra_class="", hidden=False, track_id=None):
    sid = section_id or ("shelf-" + slugify(text(title_html)))
    head_dot = f'<span class="dot" style="--dot:{dot}"></span>' if dot else ""
    count_html = f'<span class="shelf__count">{esc(count)}</span>' if count else ""
    more_html = (
        f'<a class="shelf__more" href="{esc(more_href)}">{more_label}{icon("chevron-right", "i i--sm")}</a>'
        if more_href else ""
    )
    track_attr = f' id="{track_id}"' if track_id else ""
    id_attr = f' id="{section_id}"' if section_id else ""
    return (
        f'<section class="shelf {extra_class}" aria-labelledby="{sid}-title"{" hidden" if hidden else ""}{id_attr}>'
        f'<div class="shelf__head"><h2 class="shelf__title" id="{sid}-title">{head_dot}{title_html}</h2>{count_html}'
        f'<span class="shelf__spacer"></span>{more_html}'
        f'<div class="shelf__nav"><button class="icon-btn icon-btn--sm" type="button" data-shelf-prev aria-label="Scroll left">{icon("chevron-left", "i i--sm")}</button>'
        f'<button class="icon-btn icon-btn--sm" type="button" data-shelf-next aria-label="Scroll right">{icon("chevron-right", "i i--sm")}</button></div></div>'
        f'<div class="shelf__track" data-shelf-track{track_attr}>{cards_html}</div></section>'
    )


# ---------------------------------------------------------------------------
# Ad slots (keys and script hosts are fixed - see ads.txt / network dashboards)
# ---------------------------------------------------------------------------

def ad_rect(extra_class=""):
    return (
        f'<div class="ad ad--rect {extra_class}" data-ad="banner" data-key="{ADSTERRA_RECT_KEY}" data-w="300" data-h="250">'
        f'<span class="ad__label">Advertisement</span><div class="ad__slot"></div></div>'
    )


def ad_leader(mobile="skip", extra_class=""):
    alt = ""
    if mobile == "rect":
        alt = f' data-alt-key="{ADSTERRA_RECT_KEY}" data-alt-w="300" data-alt-h="250"'
    return (
        f'<div class="ad ad--leader {extra_class}" data-ad="banner" data-key="{ADSTERRA_LEADER_KEY}" data-w="728" data-h="90" data-min-width="768"{alt}>'
        f'<span class="ad__label">Advertisement</span><div class="ad__slot"></div></div>'
    )


def ad_native(extra_class=""):
    return (
        f'<div class="ad ad--native {extra_class}" data-ad="native" data-src="{ADSTERRA_NATIVE_SRC}">'
        f'<span class="ad__label">Sponsored</span><div id="container-{ADSTERRA_NATIVE_KEY}"></div></div>'
    )


def ad_adsense(slot=AD_SLOT_BANNER):
    return (
        '<div class="ad ad--adsense"><span class="ad__label">Advertisement</span>'
        f'<ins class="adsbygoogle" style="display:block" data-ad-client="{ADSENSE_CLIENT}" data-ad-slot="{slot}" '
        'data-ad-format="auto" data-full-width-responsive="true"></ins>'
        '<script>(adsbygoogle = window.adsbygoogle || []).push({});</script></div>'
    )


# ---------------------------------------------------------------------------
# Document pieces
# ---------------------------------------------------------------------------

GA_SNIPPET = (
    f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>\n'
    "<script>\n"
    "  window.dataLayer = window.dataLayer || [];\n"
    "  function gtag(){dataLayer.push(arguments);}\n"
    "  gtag('js', new Date());\n"
    f"  gtag('config', '{GA_ID}');\n"
    "</script>"
)

SW_SNIPPET = (
    "<script>\n"
    "if ('serviceWorker' in navigator) {\n"
    "  window.addEventListener('load', () => {\n"
    "    navigator.serviceWorker.register('/service-worker.js').catch(() => {});\n"
    "  });\n"
    "}\n"
    "</script>"
)


def head(title_html, description_attr, *, canonical=None, meta_extra="", jsonld=(),
         preload_image=None, head_extra=""):
    """title_html / description_attr must already be HTML-escaped."""
    lines = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">',
        f"<title>{title_html}</title>",
    ]
    if description_attr is not None:
        lines.append(f'<meta name="description" content="{description_attr}">')
    if canonical:
        lines.append(f'<link rel="canonical" href="{canonical}">')
    if meta_extra:
        lines.append(meta_extra.strip())
    lines += [
        '<meta name="theme-color" content="#0D0E10">',
        '<link rel="icon" href="/favicon.ico" sizes="any">',
        '<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32x32.png">',
        '<link rel="icon" type="image/png" sizes="16x16" href="/assets/favicon-16x16.png">',
        '<link rel="apple-touch-icon" sizes="180x180" href="/assets/apple-touch-icon.png">',
        '<link rel="manifest" href="/manifest.json">',
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        f'<link rel="stylesheet" href="{FONTS_HREF}">',
        f'<link rel="stylesheet" href="{WORDMARK_FONT_HREF}">',
        f'<link rel="stylesheet" href="/styles.css?v={ASSET_VERSION}">',
    ]
    if preload_image:
        lines.append(f'<link rel="preload" as="image" href="{esc(preload_image)}" fetchpriority="high">')
    for block in jsonld:
        lines.append(f'<script type="application/ld+json">{block}</script>')
    lines += [
        f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>',
        '<script defer src="/_vercel/insights/script.js"></script>',
        GA_SNIPPET,
        f'<script defer src="/pixelsprout-features.js?v={ASSET_VERSION}"></script>',
        f'<script defer src="/assets/ads.js?v={ASSET_VERSION}"></script>',
        SW_SNIPPET,
    ]
    if head_extra:
        lines.append(head_extra.strip())
    lines.append("</head>")
    return "\n".join(lines)


def _count_label(total):
    if not total:
        return "Search games"
    rounded = (total // 100) * 100 if total >= 200 else total
    return f"Search {rounded:,}+ games" if total >= 200 else f"Search {total} games"


def topbar(total_games=None):
    return (
        '<a class="skip-link" href="#main">Skip to content</a>\n'
        '<header class="topbar"><div class="topbar__inner">'
        f'<button class="icon-btn menu-btn" type="button" data-menu-open aria-controls="rail" aria-expanded="false" aria-label="Open menu">{icon("menu")}</button>'
        '<a class="wordmark" href="/" aria-label="Pixelsprout home"><img src="/assets/logo-icon.png" width="28" height="28" alt=""><span>PIXEL<b>SPROUT</b></span></a>'
        f'<button class="search-trigger" type="button" data-search-open aria-label="Search games">{icon("search")}<span>{_count_label(total_games)}</span><kbd>/</kbd></button>'
        '<div class="topbar__actions">'
        f'<button class="icon-btn" type="button" data-open-panel="favorites" aria-label="Favorites">{icon("heart")}<span class="count-badge" data-count="favorites" hidden></span></button>'
        f'<button class="icon-btn" type="button" data-open-panel="recent" aria-label="Recently played">{icon("clock")}<span class="count-badge" data-count="recent" hidden></span></button>'
        "</div></div></header>"
    )


def _rail_link(href, icon_name, label, current=False):
    cur = ' aria-current="page"' if current else ""
    return (
        f'<a class="rail__link" href="{href}" aria-label="{esc(label)}" title="{esc(label)}"{cur}>'
        f'{icon(icon_name)}<span class="rail__text">{esc(label)}</span></a>'
    )


def rail(active=None):
    genres = []
    for g in RAIL_GENRES:
        url = category_url(g)
        if url:
            genres.append(_rail_link(url, genre_icon(g), pretty_genre(g), current=(active == url)))
    return (
        '<nav class="rail" id="rail" aria-label="Browse">'
        f'<div class="rail__head"><strong>Browse</strong><button class="icon-btn" type="button" data-menu-close aria-label="Close menu">{icon("x")}</button></div>'
        + _rail_link("/", "home", "Home", current=(active == "/"))
        + _rail_link("/all-games/", "list", "All games A–Z", current=(active == "/all-games/"))
        + f'<button class="rail__link" type="button" data-open-panel="favorites" aria-label="Favorites" title="Favorites">{icon("heart")}<span class="rail__text">Favorites</span><span class="rail__count" data-count="favorites"></span></button>'
        + f'<button class="rail__link" type="button" data-open-panel="recent" aria-label="Recently played" title="Recently played">{icon("clock")}<span class="rail__text">Recently played</span><span class="rail__count" data-count="recent"></span></button>'
        + '<div class="rail__label">Genres</div><div class="rail__genres">'
        + "".join(genres)
        + "</div>"
        + _rail_link("/#all-genres", "grid", "All genres")
        + '<div class="rail__label">Originals</div>'
        + _rail_link("/cold-read/", "eye", "Cold Read", current=(active == "/cold-read/"))
        + _rail_link("/gift-file/", "gift", "Guess It Box", current=(active == "/gift-file/"))
        + '<div class="rail__label">Read</div>'
        + _rail_link("/guides/", "book", "Game guides", current=(active == "/guides/"))
        + "</nav>"
        '<div class="scrim" data-scrim></div>'
    )


_collection_links = None


def collection_links(limit=6):
    global _collection_links
    if _collection_links is None:
        base = os.path.join(ROOT, "games-like")
        preferred = ["best-puzzle-games", "best-racing-games", "best-multiplayer-games",
                     "best-games-for-kids", "subway-surfers", "minecraft", "geometry-dash", "chess"]
        names = []
        if os.path.isdir(base):
            existing = {n for n in os.listdir(base) if os.path.isfile(os.path.join(base, n, "index.html"))}
            names = [n for n in preferred if n in existing]
        _collection_links = names
    out = []
    for name in _collection_links[:limit]:
        label = name.replace("-", " ")
        if label.startswith("best "):
            label = "Best " + label[5:]
        else:
            label = "Games like " + label.title()
        out.append((f"/games-like/{name}/", label[0].upper() + label[1:]))
    return out


def footer():
    year = datetime.date.today().year
    genre_items = []
    for g in FOOTER_GENRES:
        url = category_url(g)
        if url:
            genre_items.append(f'<li><a href="{url}">{esc(pretty_genre(g))} games</a></li>')
    coll_items = [f'<li><a href="{href}">{esc(label)}</a></li>' for href, label in collection_links()]
    coll_items.append('<li><a href="/all-games/">All games A–Z</a></li>')
    coll_items.append('<li><a href="/guides/">Game guides</a></li>')
    return (
        '<footer class="footer"><div class="footer__inner">'
        '<div class="footer__brand"><a class="wordmark" href="/" aria-label="Pixelsprout home"><img src="/assets/logo-icon.png" width="28" height="28" alt="" loading="lazy"><span>PIXEL<b>SPROUT</b></span></a>'
        "<p>A free library of browser games, kept tidy by hand. Nothing to download, no account to make. Pick something and play.</p></div>"
        f'<nav aria-label="Popular genres"><h2>Genres</h2><ul>{"".join(genre_items)}</ul></nav>'
        f'<nav aria-label="Collections"><h2>Collections</h2><ul>{"".join(coll_items)}</ul></nav>'
        '<nav aria-label="Pixelsprout"><h2>Pixelsprout</h2><ul>'
        '<li><a href="/about.html">About</a></li><li><a href="/contact.html">Contact</a></li>'
        '<li><a href="/privacy.html">Privacy</a></li><li><a href="/terms.html">Terms</a></li></ul></nav>'
        "</div>"
        f'<div class="footer__base"><span>© {year} Pixelsprout</span><span>Some games provided via GamePix and GameMonetize.</span></div>'
        "</footer>"
    )


def page(head_html, main_html, *, body_attrs="", active=None, total_games=None, after_main=""):
    return (
        f"{head_html}\n<body{(' ' + body_attrs) if body_attrs else ''}>\n"
        f"{topbar(total_games)}\n"
        f'<div class="shell">{rail(active)}\n'
        f'<main id="main" class="main" tabindex="-1">\n{main_html}\n</main></div>\n'
        f"{footer()}\n{after_main}</body>\n</html>\n"
    )
