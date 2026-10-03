"""Page renderers and extractors built on site_shell.

render_* functions produce complete HTML documents. extract_* functions read
an existing page (old template or current template) back into the same
fields, which is what lets migrate-ui.py re-run safely over pages it has
already converted.
"""

import datetime
import json
import os
import re

import site_shell as S
from site_shell import esc, text

DOMAIN = S.DOMAIN


def _first(pattern, source, flags=re.DOTALL, default=""):
    m = re.search(pattern, source, flags)
    return m.group(1) if m else default


def _region(name, source):
    return _first(rf"<!--ps:{name}-->(.*?)<!--/ps:{name}-->", source)


def _head_part(html_doc):
    return html_doc.split("</head>", 1)[0]


def _jsonld_blocks(html_doc):
    return re.findall(r'<script type="application/ld\+json">(.*?)</script>', _head_part(html_doc), re.DOTALL)


def _og_meta(html_doc):
    head = _head_part(html_doc)
    tags = re.findall(r'<meta (?:property|name)="(?:og|twitter):[^"]+" content="[^"]*"\s*/?>', head)
    return "\n".join(tags)


def _body_attr(html_doc, name):
    body = _first(r"<body([^>]*)>", html_doc)
    return _first(rf'\s{re.escape(name)}="([^"]*)"', body)


def fix_jsonld_urls(block):
    """Old game pages carry Windows-path URLs like /games/games\\\\slug.html."""
    return re.sub(r"/games/games\\\\+", "/games/", block)


# ---------------------------------------------------------------------------
# Similar games
# ---------------------------------------------------------------------------

_groups_cache = {}


def _catalog_groups(catalog):
    key = id(catalog)
    if key not in _groups_cache:
        groups = {}
        for g in catalog:
            groups.setdefault(S.primary_category(g.get("category", "")), []).append(g)
        _groups_cache.clear()
        _groups_cache[key] = groups
    return _groups_cache[key]


def similar_games(slug, category, catalog, count=18):
    primary = S.primary_category(category)
    same = [g for g in _catalog_groups(catalog).get(primary, []) if g["slug"] != slug]
    same.sort(key=lambda g: (not g.get("thumbnail"), S.stable_hash(slug + g["slug"])))
    picks = same[:count]
    if len(picks) < count:
        taken = {g["slug"] for g in picks} | {slug}
        rest = [g for g in catalog if g["slug"] not in taken and g.get("thumbnail")]
        rest.sort(key=lambda g: S.stable_hash(slug + "~" + g["slug"]))
        picks += rest[: count - len(picks)]
    return picks


# ---------------------------------------------------------------------------
# Game pages
# ---------------------------------------------------------------------------

def orientation_lock_js(orientation):
    orientation = (orientation or "").lower()
    if orientation == "portrait":
        return ("if (screen.orientation && screen.orientation.lock) { "
                "screen.orientation.lock('portrait-primary').catch(() => {}); }")
    if orientation == "landscape":
        return ("if (screen.orientation && screen.orientation.lock) { "
                "screen.orientation.lock('landscape').catch(() => {}); }")
    return ""


def fullscreen_onclick(lock_js=""):
    code = (
        "\n      const f = document.querySelector('.embed-frame-wrap');"
        "\n      const req = f.requestFullscreen || f.webkitRequestFullscreen || f.msRequestFullscreen;"
        "\n      if (req) req.call(f);"
        "\n      if (typeof gtag === 'function') { gtag('event', 'fullscreen_click', { game_title: document.title }); }"
    )
    if lock_js:
        code += "\n      " + lock_js
    return code + "\n    "


def game_jsonld(game):
    schema = {
        "@context": "https://schema.org",
        "@type": "VideoGame",
        "name": game["title"],
        "description": game.get("description", ""),
        "genre": game["category"],
        "url": f"{DOMAIN}/games/{game['slug']}.html",
        "applicationCategory": "Game",
        "operatingSystem": "Web Browser",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
    }
    if game.get("thumbnail"):
        schema["image"] = game["thumbnail"]
    crumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{DOMAIN}/"},
            {"@type": "ListItem", "position": 2, "name": game["category"], "item": f"{DOMAIN}/games/{game['slug']}.html"},
            {"@type": "ListItem", "position": 3, "name": game["title"], "item": f"{DOMAIN}/games/{game['slug']}.html"},
        ],
    }
    return [json.dumps(schema), json.dumps(crumb)]


def new_game_fields(game):
    """Fields for a brand-new game coming from a provider feed."""
    title = game["title"]
    desc_text = text(game.get("description", ""))
    return {
        "slug": game["slug"],
        "title": title,
        "title_tag": f"{esc(title)} — Pixelsprout",
        "meta_desc": esc(f"Play {title} free online, no download needed."),
        "category": game["category"],
        "embed_url": game["embed_url"],
        "thumbnail": game.get("thumbnail", ""),
        "description_html": esc(desc_text),
        "onclick": fullscreen_onclick(orientation_lock_js(game.get("orientation"))),
        "jsonld": game_jsonld(game),
    }


def extract_game_page(doc, slug):
    """Returns the fields of an iframe game page, or None for built-in games."""
    embed = _first(r'<iframe src="([^"]*)"', doc)
    if not embed:
        return None
    title_html = _first(r'<h1 class="(?:game-title|game-bar__title)">(.*?)</h1>', doc)
    if _body_attr(doc, "data-page") == "game":
        category = text(_body_attr(doc, "data-genre"))
        thumbnail = text(_body_attr(doc, "data-thumbnail"))
        description = _region("desc", doc)
    else:
        category = text(_first(r'<div class="game-meta">(.*?)</div>', doc))
        thumbnail = text(_first(r'data-thumbnail="([^"]*)"', doc))
        description = _first(r'<p class="how-to">(.*?)</p>', doc).strip()
    onclick = _first(r'fullscreen-btn"[^>]*?onclick="([^"]*)"', doc)
    fields = {
        "slug": slug,
        "title": S.clean_title(text(title_html)),
        "title_tag": _first(r"<title>(.*?)</title>", doc).strip(),
        "meta_desc": _first(r'<meta name="description" content="([^"]*)"', doc),
        "category": category or "Arcade",
        "embed_url": embed,
        "thumbnail": thumbnail,
        "description_html": description,
        "onclick": onclick or fullscreen_onclick(),
        "jsonld": [fix_jsonld_urls(b) for b in _jsonld_blocks(doc)],
    }
    if not fields["thumbnail"]:
        for block in fields["jsonld"]:
            try:
                img = json.loads(block).get("image")
            except (ValueError, AttributeError):
                img = None
            if img:
                fields["thumbnail"] = img
                break
    return fields


GUIDE_LABELS = [
    ("tips", "Tips & strategy", "lightbulb"),
    ("controls", "Controls", "keyboard"),
    ("beginner-guide", "Beginner's guide", "flag-start"),
    ("faq", "FAQ", "help"),
    ("similar", "Games like this", "layers"),
]


def render_game_page(f, catalog, guides=None, total_games=None):
    slug, title, category = f["slug"], f["title"], f["category"]
    genre_label = S.pretty_genre(category)
    genre_href = S.category_url(category)
    thumb = f.get("thumbnail") or ""
    similar = similar_games(slug, category, catalog, 18)
    rail_list, shelf_list = similar[:6], similar[6:18]
    if len(shelf_list) < 6:
        shelf_list = similar[:12]

    description = (f.get("description_html") or "").strip()
    if not text(description):
        description = esc(f"{title} is a free {genre_label.lower()} game you can play right here in your browser — no download, no sign-up.")

    og = [
        '<meta property="og:type" content="website">',
        f'<meta property="og:title" content="{esc(title)} — Pixelsprout">',
        f'<meta property="og:description" content="{f["meta_desc"]}">',
        f'<meta property="og:url" content="{DOMAIN}/games/{esc(slug)}.html">',
    ]
    if thumb:
        og.append(f'<meta property="og:image" content="{esc(thumb)}">')
    og.append('<meta name="twitter:card" content="summary">')

    head = S.head(
        f["title_tag"], f["meta_desc"],
        meta_extra="\n".join(og),
        jsonld=f["jsonld"],
        head_extra='<link rel="preconnect" href="https://img.gamepix.com">\n<link rel="preconnect" href="https://img.gamemonetize.com">',
    )

    crumb_items = [("Home", "/")]
    if genre_href:
        crumb_items.append((esc(genre_label), genre_href))
    crumb_items.append((esc(title), None))

    chip = (
        f'<a class="chip" href="{genre_href}"><span class="dot" style="--dot:{S.genre_color(category)}"></span>{esc(genre_label)}</a>'
        if genre_href else
        f'<span class="chip"><span class="dot" style="--dot:{S.genre_color(category)}"></span>{esc(genre_label)}</span>'
    )

    mini = "".join(
        f'<li><a href="/games/{esc(g["slug"])}.html"><img src="{esc(S.thumb_of(g))}" alt="" width="48" height="48" loading="lazy" decoding="async">'
        f'<span><b>{esc(g["title"])}</b><small>{esc(S.pretty_genre(g.get("category", "")))}</small></span></a></li>'
        for g in rail_list
    )

    guides_html = ""
    if guides:
        rows = []
        for key, label, icon_name in GUIDE_LABELS:
            url = guides.get(key)
            if not url:
                continue
            shown = f"Games like {title}" if key == "similar" else label
            rows.append(
                f'<li><a href="{esc(url)}">{S.icon(icon_name)}<span class="link-list__label">{esc(shown)}</span>{S.icon("chevron-right", "i i--sm")}</a></li>'
            )
        if rows:
            guides_html = (
                f'<section aria-labelledby="guides-title"><h2 class="block__title" id="guides-title">Guides for {esc(title)}</h2>'
                f'<ul class="link-list">{"".join(rows)}</ul></section>'
            )

    shelf_cards = "".join(S.card(g) for g in shelf_list)
    more_like = S.shelf("More like this", shelf_cards, more_href=genre_href,
                        more_label=f"All {esc(genre_label.lower())} games" if genre_href else "See all",
                        section_id="more-like-this")

    main = f"""<div class="game-layout">
<div class="game-main">
{S.crumbs(crumb_items)}
<div class="stage"><div class="embed-frame-wrap"><iframe src="{f['embed_url']}" allow="fullscreen; autoplay; screen-orientation;" scrolling="no" allowfullscreen title="{esc(title)}"></iframe></div></div>
<div class="game-bar">
<div class="game-bar__info"><h1 class="game-bar__title">{esc(title)}</h1>{chip}</div>
<div class="game-bar__actions">
<button class="btn btn--ghost fullscreen-btn" type="button" onclick="{f['onclick']}">{S.icon('maximize')}<span>Fullscreen</span></button>
<button class="icon-btn icon-btn--outline" type="button" data-fav aria-pressed="false" aria-label="Add to favorites">{S.icon('heart')}</button>
<button class="icon-btn icon-btn--outline" type="button" data-share aria-label="Share this game">{S.icon('share')}</button>
</div>
</div>
</div>
<aside class="game-rail" aria-label="Sponsored and related games">
{S.ad_rect()}
<div class="game-rail__more"><h2 class="eyebrow">More like this</h2><ul class="mini-list">{mini}</ul></div>
</aside>
<div class="game-body">
<section class="game-about" aria-labelledby="about-title">
<h2 id="about-title">About {esc(title)}</h2>
<p class="how-to"><!--ps:desc-->{description}<!--/ps:desc--></p>
<div class="facts"><span class="chip">Free to play</span><span class="chip">No download</span><span class="chip">Plays in your browser</span></div>
</section>
{S.ad_native()}
{guides_html}
{S.ad_adsense(S.AD_SLOT_BANNER)}
{more_like}
{S.ad_leader(mobile="skip")}
{S.ad_adsense(S.AD_SLOT_RIBBON)}
</div>
</div>"""

    body_attrs = (
        f'class="game-page" data-page="game" data-slug="{esc(slug)}" data-title="{esc(title)}" '
        f'data-genre="{esc(category)}" data-thumbnail="{esc(thumb)}"'
    )
    return S.page(head, main, body_attrs=body_attrs, active=genre_href, total_games=total_games)


# ---------------------------------------------------------------------------
# Guide pages
# ---------------------------------------------------------------------------

def _parse_crumbs_legacy(fragment):
    items = [(label.strip(), href) for href, label in re.findall(r'<a href="([^"]*)"[^>]*>(.*?)</a>', fragment, re.DOTALL)]
    tail = re.sub(r"<a [^>]*>.*?</a>", "", fragment, flags=re.DOTALL)
    tail = tail.replace("/", " ").strip()
    if tail:
        items.append((tail, None))
    return items


def _parse_crumbs_new(fragment):
    items = [(label.strip(), href) for href, label in re.findall(r'<a href="([^"]*)">(.*?)</a>', fragment, re.DOTALL)]
    cur = _first(r'<span aria-current="page">(.*?)</span>', fragment)
    if cur:
        items.append((cur.strip(), None))
    return items


def _normalize_crumbs(items):
    out = []
    for label, href in items:
        if href in ("/index.html", "index.html", "../index.html"):
            href = "/"
        out.append((label, href))
    return out


def _parse_card_links(fragment):
    """Game links rendered as legacy similar-cards or current cards."""
    games = []
    for href, inner in re.findall(r'<a class="(?:similar-card|card)[^"]*" href="([^"]*)"[^>]*>(.*?)</a>', fragment, re.DOTALL):
        m = re.match(r"/games/([^/]+)\.html$", href)
        if not m:
            continue
        img = _first(r'<img src="([^"]*)"', inner)
        title = _first(r'<span class="card__title">(.*?)</span>', inner) or _first(r"<span>(.*?)</span>", inner)
        games.append({"slug": m.group(1), "title": text(title), "thumbnail": "" if img.endswith("logo-icon.png") else img})
    return games


def extract_guide_page(doc):
    f = {
        "title_tag": _first(r"<title>(.*?)</title>", doc).strip(),
        "meta_desc": _first(r'<meta name="description" content="([^"]*)"', doc),
        "canonical": _first(r'<link rel="canonical" href="([^"]*)"', doc),
        "og": _og_meta(doc),
        "jsonld": _jsonld_blocks(doc),
    }
    if _body_attr(doc, "data-page") == "guide":
        f["crumbs"] = _parse_crumbs_new(_first(r'<nav class="crumbs"[^>]*>(.*?)</nav>', doc))
        f["h1"] = _first(r'<h1 class="page-title">(.*?)</h1>', doc)
        f["eyebrow"] = _region("eyebrow", doc)
        f["game_slug"] = _body_attr(doc, "data-game-slug")
        f["game_title"] = text(_body_attr(doc, "data-game-title"))
        f["genre"] = text(_body_attr(doc, "data-genre"))
        f["thumbnail"] = text(_body_attr(doc, "data-thumbnail"))
        f["body"] = _region("body", doc)
        f["siblings"] = re.findall(r'<a href="([^"]*)">.*?<span class="link-list__label">(.*?)</span>', _region("siblings", doc), re.DOTALL)
        f["related"] = _parse_card_links(_region("related", doc))
        return f

    f["crumbs"] = _normalize_crumbs(_parse_crumbs_legacy(_first(r'<div class="breadcrumb"[^>]*>(.*?)</div>', doc)))
    f["h1"] = _first(r'<h1 class="game-title">(.*?)</h1>', doc)
    f["eyebrow"] = _first(r'<div class="game-meta">(.*?)</div>', doc)
    back = re.search(r'<a class="back-link" href="/games/([^"]+)\.html">&larr; back to (.*?)</a>', doc)
    f["game_slug"] = back.group(1) if back else ""
    f["game_title"] = text(back.group(2)) if back else ""
    genre = text(f["eyebrow"]).split("·")[-1].strip()
    f["genre"] = genre
    frame = doc.split('<div class="game-board-frame">', 1)[-1]
    img = _first(r'<img src="([^"]*)"', frame)
    f["thumbnail"] = "" if (not img or img.endswith("logo-icon.png")) else img
    body = _first(r'<article class="guide-body"[^>]*>(.*?)</article>', doc).strip()
    body = re.sub(r'\s+style="[^"]*"', "", body)
    body = re.sub(r'<p>\s*<a href="(/[^"]+/)">Browse more (.*?) &rarr;</a></p>', r'<p><a href="\1">Browse more \2 &rarr;</a></p>', body)
    f["body"] = body
    blocks = re.findall(r'<div class="similar-games">(.*?)</div>\s*</div>', doc, re.DOTALL)
    siblings, related = [], []
    for block in blocks:
        if "More about" in block:
            siblings = re.findall(r'<a class="similar-card" href="([^"]*)"><span>(.*?)</span></a>', block)
        else:
            related = _parse_card_links(block)
    f["siblings"] = siblings
    f["related"] = related
    return f


def render_guide_page(f, catalog_by_slug=None, total_games=None):
    catalog_by_slug = catalog_by_slug or {}
    game_slug = f.get("game_slug", "")
    game_title = f.get("game_title", "")
    genre = f.get("genre", "")
    thumb = f.get("thumbnail") or ""
    game_entry = catalog_by_slug.get(game_slug, {})
    if not thumb:
        thumb = game_entry.get("thumbnail", "")
    genre_label = S.pretty_genre(genre) if genre else ""

    head = S.head(f["title_tag"], f["meta_desc"], canonical=f.get("canonical") or None,
                  meta_extra=f.get("og", ""), jsonld=f.get("jsonld", []))

    game_card = ""
    if game_slug:
        game_card = (
            '<div class="game-card">'
            f'<a class="game-card__art" href="/games/{esc(game_slug)}.html" tabindex="-1" aria-hidden="true">'
            f'<img src="{esc(thumb or S.FALLBACK_THUMB)}" alt="" width="88" height="88" decoding="async"></a>'
            f'<div class="game-card__body"><span class="game-card__title">{esc(game_title)}</span>'
            f'<span class="game-card__meta">{esc(genre_label)}{" · " if genre_label else ""}Free to play</span></div>'
            f'<a class="btn btn--primary" href="/games/{esc(game_slug)}.html">{S.icon("play", "i i--sm")}Play now</a>'
            "</div>"
        )

    sibling_rows = []
    icons = {"Tips": "lightbulb", "Controls": "keyboard", "Beginner": "flag-start", "FAQ": "help", "Games Like": "layers"}
    for href, label in f.get("siblings", []):
        icon_name = next((v for k, v in icons.items() if text(label).startswith(k)), "book")
        sibling_rows.append(
            f'<li><a href="{esc(href)}">{S.icon(icon_name)}<span class="link-list__label">{label}</span>{S.icon("chevron-right", "i i--sm")}</a></li>'
        )
    siblings_html = ""
    if sibling_rows:
        siblings_html = (
            f'<section class="block" aria-labelledby="more-about"><h2 class="block__title" id="more-about">More about {esc(game_title)}</h2>'
            f'<ul class="link-list"><!--ps:siblings-->{"".join(sibling_rows)}<!--/ps:siblings--></ul></section>'
        )

    related_cards = []
    for g in f.get("related", []):
        entry = dict(catalog_by_slug.get(g["slug"], {}))
        entry.setdefault("slug", g["slug"])
        entry["title"] = g.get("title") or entry.get("title", g["slug"])
        entry["thumbnail"] = g.get("thumbnail") or entry.get("thumbnail", "")
        related_cards.append(S.card(entry))
    related_html = ""
    if related_cards:
        related_html = S.shelf("Play something similar", "<!--ps:related-->" + "".join(related_cards) + "<!--/ps:related-->",
                               more_href=S.category_url(genre) if genre else None, section_id="related",
                               extra_class="block")

    main = f"""<article class="reading">
{S.crumbs(f['crumbs'])}
<header class="page-head">
<p class="eyebrow"><!--ps:eyebrow-->{f.get('eyebrow', '')}<!--/ps:eyebrow--></p>
<h1 class="page-title">{f['h1']}</h1>
</header>
{game_card}
{S.ad_adsense(S.AD_SLOT_BANNER)}
<div class="prose"><!--ps:body-->{f['body']}<!--/ps:body--></div>
<div class="block">{S.ad_native()}</div>
{siblings_html}
{related_html}
<div class="block">{S.ad_rect()}</div>
</article>"""

    body_attrs = (
        f'class="guide-page" data-page="guide" data-game-slug="{esc(game_slug)}" data-game-title="{esc(game_title)}" '
        f'data-genre="{esc(genre)}" data-thumbnail="{esc(thumb)}"'
    )
    return S.page(head, main, body_attrs=body_attrs, active="/guides/", total_games=total_games)


# ---------------------------------------------------------------------------
# Collection pages (games-like/*)
# ---------------------------------------------------------------------------

def extract_collection_page(doc):
    f = {
        "title_tag": _first(r"<title>(.*?)</title>", doc).strip(),
        "meta_desc": _first(r'<meta name="description" content="([^"]*)"', doc),
        "canonical": _first(r'<link rel="canonical" href="([^"]*)"', doc),
        "og": _og_meta(doc),
        "jsonld": _jsonld_blocks(doc),
    }
    if _body_attr(doc, "data-page") == "collection":
        f["h1"] = _first(r'<h1 class="page-title">(.*?)</h1>', doc)
        f["intro"] = _region("intro", doc)
        f["games"] = _parse_card_links(_region("games", doc))
    else:
        f["h1"] = _first(r'<h1 class="game-title">(.*?)</h1>', doc)
        f["intro"] = _first(r'<div class="game-board-frame">\s*<p[^>]*>(.*?)</p>', doc).strip()
        f["games"] = _parse_card_links(_first(r'<div class="similar-games-grid">(.*?)</div>', doc))
    return f


def render_collection_page(f, catalog_by_slug=None, total_games=None):
    catalog_by_slug = catalog_by_slug or {}
    head = S.head(f["title_tag"], f["meta_desc"], canonical=f.get("canonical") or None,
                  meta_extra=f.get("og", ""), jsonld=f.get("jsonld", []))
    cards = []
    for g in f["games"]:
        entry = dict(catalog_by_slug.get(g["slug"], {}))
        entry.setdefault("slug", g["slug"])
        entry["title"] = g.get("title") or entry.get("title", g["slug"])
        entry["thumbnail"] = g.get("thumbnail") or entry.get("thumbnail", "")
        cards.append(S.card(entry))
    main = f"""<div class="reading reading--wide">
{S.crumbs([("Home", "/"), (f['h1'], None)])}
<header class="page-head">
<p class="eyebrow">Collection</p>
<h1 class="page-title">{f['h1']}</h1>
<p class="page-lede"><!--ps:intro-->{f['intro']}<!--/ps:intro--></p>
<p class="page-meta">{len(cards)} games</p>
</header>
{S.ad_adsense(S.AD_SLOT_BANNER)}
<div class="grid"><!--ps:games-->{''.join(cards)}<!--/ps:games--></div>
<div class="block">{S.ad_native()}</div>
<div class="block">{S.ad_rect()}</div>
</div>"""
    return S.page(head, main, body_attrs='class="collection-page" data-page="collection"', total_games=total_games)


# ---------------------------------------------------------------------------
# Legal / company pages
# ---------------------------------------------------------------------------

def extract_legal_page(doc):
    f = {
        "title_tag": _first(r"<title>(.*?)</title>", doc).strip(),
        "meta_desc": _first(r'<meta name="description" content="([^"]*)"', doc),
        "canonical": _first(r'<link rel="canonical" href="([^"]*)"', doc),
        "og": _og_meta(doc),
        "jsonld": _jsonld_blocks(doc),
    }
    if _body_attr(doc, "data-page") == "legal":
        f["h1"] = _first(r'<h1 class="page-title">(.*?)</h1>', doc)
        f["body"] = _region("body", doc)
        return f
    inner = _first(r'<div class="legal">(.*?)</div>\s*</body>', doc)
    inner = re.sub(r'<div class="legal-nav">.*?</div>', "", inner, flags=re.DOTALL)
    f["h1"] = _first(r"<h1>(.*?)</h1>", inner)
    inner = re.sub(r"<h1>.*?</h1>", "", inner, count=1, flags=re.DOTALL)
    inner = re.sub(r'<p><a href="/">← back to Pixelsprout</a></p>', "", inner)
    f["body"] = inner.strip()
    return f


def render_legal_page(f, total_games=None):
    head = S.head(f["title_tag"], f["meta_desc"], canonical=f.get("canonical") or None,
                  meta_extra=f.get("og", ""), jsonld=f.get("jsonld", []))
    main = f"""<article class="reading">
{S.crumbs([("Home", "/"), (f['h1'], None)])}
<header class="page-head"><h1 class="page-title">{f['h1']}</h1></header>
<div class="prose"><!--ps:body-->{f['body']}<!--/ps:body--></div>
</article>"""
    return S.page(head, main, body_attrs='class="legal-page" data-page="legal"', total_games=total_games)


# ---------------------------------------------------------------------------
# Legacy-body pages (tool pages, built-in games): new shell, original body
# ---------------------------------------------------------------------------

_OLD_FONT_LINK = re.compile(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?family=Press\+Start\+2P[^"]*">\n?')
_OLD_STYLES_LINK = re.compile(r'<link rel="stylesheet" href="(?:\.\./|/)?styles\.css(?:\?v=[^"]*)?">')


def wrap_legacy_page(doc, total_games=None, active=None):
    doc = re.sub(r"<!--ps:top-->.*?<!--/ps:top-->\n?", "", doc, flags=re.DOTALL)
    doc = re.sub(r"<!--ps:bottom-->.*?<!--/ps:bottom-->\n?", "", doc, flags=re.DOTALL)
    doc = re.sub(r'<link rel="stylesheet" href="' + re.escape(S.FONTS_HREF) + r'">\n?', "", doc)
    doc = re.sub(r'<link rel="stylesheet" href="' + re.escape(S.WORDMARK_FONT_HREF) + r'">\n?', "", doc)
    doc = _OLD_FONT_LINK.sub("", doc)
    doc = fix_jsonld_urls(doc)
    doc = re.sub(r'<link rel="preconnect" href="https://fonts\.(?:googleapis|gstatic)\.com"(?: crossorigin)?>\n?', "", doc)
    fonts = (
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        f'<link rel="stylesheet" href="{S.FONTS_HREF}">\n'
        f'<link rel="stylesheet" href="{S.WORDMARK_FONT_HREF}">\n'
        f'<link rel="stylesheet" href="/styles.css?v={S.ASSET_VERSION}">'
    )
    doc, n = _OLD_STYLES_LINK.subn(lambda m: fonts, doc, count=1)
    if not n:
        doc = doc.replace("</head>", fonts + "\n</head>", 1)
    if "/assets/ads.js" not in doc:
        doc = doc.replace("</head>", f'<script defer src="/assets/ads.js?v={S.ASSET_VERSION}"></script>\n</head>', 1)
    doc = re.sub(r'<script defer src="(?:\.\./|/)pixelsprout-features\.js(?:\?v=[^"]*)?"></script>',
                 f'<script defer src="/pixelsprout-features.js?v={S.ASSET_VERSION}"></script>', doc)

    top = (
        "<!--ps:top-->\n" + S.topbar(total_games) + "\n"
        f'<div class="shell">{S.rail(active)}\n<main id="main" class="main" tabindex="-1">\n'
        "<!--/ps:top-->\n"
    )
    bottom = "<!--ps:bottom-->\n</main></div>\n" + S.footer() + "\n<!--/ps:bottom-->\n"
    doc = re.sub(r"(<body[^>]*>\n?)", lambda m: m.group(1) + top, doc, count=1)
    idx = doc.rfind("</body>")
    doc = doc[:idx] + bottom + doc[idx:]
    return doc


# ---------------------------------------------------------------------------
# Category pages
# ---------------------------------------------------------------------------

def category_intro(category, count):
    name = S.pretty_genre(category).lower()
    return (
        f"Browse {count} free {name} games, playable instantly in your browser. "
        f"No downloads, no accounts, no waiting — just click and play. New {name} "
        f"games are added regularly, so check back for more."
    )


def render_category_page(category, games, all_categories, total_games=None, newness=None):
    slug = S.slugify(category)
    canonical_url = f"{DOMAIN}/{slug}/"
    count = len(games)
    label = S.pretty_genre(category)
    title = f"{category} Games - Free Online, No Download | Pixelsprout"
    description = f"Play {count} free {category.lower()} games online at Pixelsprout. No downloads, no accounts - instant browser play."
    breadcrumb_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{DOMAIN}/"},
            {"@type": "ListItem", "position": 2, "name": category, "item": canonical_url},
        ],
    })
    og = "\n".join([
        '<meta property="og:type" content="website">',
        f'<meta property="og:url" content="{canonical_url}">',
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(description)}">',
        f'<meta property="og:image" content="{DOMAIN}/assets/og-banner.jpg">',
    ])
    head = S.head(esc(title), esc(description), canonical=canonical_url, meta_extra=og, jsonld=[breadcrumb_schema],
                  head_extra='<link rel="preconnect" href="https://img.gamepix.com">\n<link rel="preconnect" href="https://img.gamemonetize.com">')

    page_size = 60
    cards = "".join(
        S.card(g, show_meta=False, index=i, extra_class="is-more" if i >= page_size else "",
               newness=(newness or {}).get(g["slug"], i))
        for i, g in enumerate(games)
    )
    related = []
    for other, other_count in all_categories:
        if S.slugify(other) == slug:
            continue
        url = S.category_url(other)
        if url and url != f"/{slug}/":
            related.append(f'<a class="chip" href="{url}"><span class="dot" style="--dot:{S.genre_color(other)}"></span>{esc(S.pretty_genre(other))}</a>')
    related_html = "".join(related[:24])

    main = f"""{S.crumbs([("Home", "/"), (esc(label), None)])}
<header class="page-head">
<p class="eyebrow"><span class="dot" style="--dot:{S.genre_color(category)}"></span> Genre</p>
<h1 class="page-title">{esc(label)} games</h1>
<p class="page-lede">{esc(category_intro(category, count))}</p>
</header>
<div class="catalog-bar" data-catalog-bar>
<label class="field"><span class="visually-hidden">Filter {esc(label)} games</span>{S.icon('search')}<input type="search" data-catalog-filter placeholder="Filter {count} {esc(label.lower())} games" autocomplete="off"></label>
<div class="segmented" role="group" aria-label="Sort games">
<button type="button" data-sort="popular" aria-pressed="true">Popular</button>
<button type="button" data-sort="new" aria-pressed="false">Newest</button>
<button type="button" data-sort="az" aria-pressed="false">A–Z</button>
</div>
<span class="catalog-bar__count" data-catalog-count>{count} games</span>
</div>
<div class="grid grid--genre" id="catalog" data-catalog data-page-size="{page_size}">{cards}</div>
<p class="empty-state" data-catalog-empty hidden>No {esc(label.lower())} games match that. Try a shorter word, or <button class="btn btn--quiet" type="button" data-search-open>search every game</button>.</p>
<div class="load-more"{" hidden" if count <= page_size else ""}><button class="btn btn--ghost" type="button" data-load-more>Show more games</button></div>
<div class="block">{S.ad_native()}</div>
<section class="related-genres" aria-labelledby="more-genres"><h2 class="section-title" id="more-genres">More genres</h2><div class="chips">{related_html}</div></section>
<div class="block">{S.ad_leader(mobile="rect")}</div>"""
    return S.page(head, main, body_attrs='class="category-page" data-page="category"', active=f"/{slug}/", total_games=total_games)


# ---------------------------------------------------------------------------
# Homepage and A–Z
# ---------------------------------------------------------------------------

HOME_SHELVES = ["Puzzle", "Arcade", "Action", "Adventure", "Sports", "Racing", "Kids", "Casual",
                "Clicker", "Shooting", "Two-Player", "Multiplayer"]

POPULAR_FALLBACK = ["subway-princess-run", "worms-zone", "uno-online", "baba-is-you",
                    "getting-over-it", "suika-world", "tank-1990", "ultimate-solitaire-classic"]


def _group_by_primary(catalog):
    groups = {}
    for g in catalog:
        groups.setdefault(S.primary_category(g.get("category", "")), []).append(g)
    return groups


def _featured_pick(featured, by_slug, today=None):
    today = today or datetime.date.today()
    usable = [f for f in featured if f.get("slug") in by_slug]
    if not usable:
        return None, None
    pick = usable[today.toordinal() % len(usable)]
    return pick, by_slug[pick["slug"]]


def render_home(catalog, featured, popular_ranked, today=None):
    by_slug = {g["slug"]: g for g in catalog}
    groups = _group_by_primary(catalog)
    total = len(catalog)
    genre_pages = []
    for cat, games in groups.items():
        url = S.category_url(cat)
        if url and len(games) >= 3:
            genre_pages.append((cat, len(games), url))
    genre_pages.sort(key=lambda x: -x[1])

    pick, hero_game = _featured_pick(featured, by_slug, today)
    used = set()
    hero_html = ""
    preload = None
    if hero_game:
        used.add(hero_game["slug"])
        art = S.thumb_of(hero_game, size=640)
        preload = art
        genre_url = S.category_url(hero_game.get("category", ""))
        genre_label = S.pretty_genre(hero_game.get("category", ""))
        chip = (f'<a class="chip" href="{genre_url}"><span class="dot" style="--dot:{S.genre_color(hero_game.get("category", ""))}"></span>{esc(genre_label)}</a>'
                if genre_url else f'<span class="chip">{esc(genre_label)}</span>')
        hero_html = f"""<section class="hero" aria-labelledby="hero-title">
<div class="hero__bg" style="background-image:url('{esc(art)}')" aria-hidden="true"></div>
<div class="hero__body">
<p class="eyebrow">Featured today</p>
<h2 class="hero__title" id="hero-title"><a href="/games/{esc(hero_game['slug'])}.html">{esc(hero_game['title'])}</a></h2>
<p class="hero__pitch">{esc(pick.get('pitch', ''))}</p>
<div class="hero__meta">{chip}<span class="chip">Free · No download</span></div>
<div class="hero__cta"><a class="btn btn--primary" href="/games/{esc(hero_game['slug'])}.html">{S.icon('play', 'i i--sm')}Play now</a>{f'<a class="btn btn--ghost" href="{genre_url}">More {esc(genre_label.lower())} games</a>' if genre_url else ''}</div>
</div>
<a class="hero__art" href="/games/{esc(hero_game['slug'])}.html" tabindex="-1" aria-hidden="true"><img src="{esc(art)}" alt="" width="640" height="400" fetchpriority="high" decoding="async"></a>
</section>"""

    ranked = [by_slug[r["slug"]] for r in (popular_ranked or []) if r.get("slug") in by_slug]
    popular = ranked[:10] if len(ranked) >= 4 else [by_slug[s] for s in POPULAR_FALLBACK if s in by_slug]
    popular = [g for g in popular if g["slug"] not in used]
    popular_cards = "".join(S.tool_card(*t) for t in S.TOOL_CARDS) + "".join(S.card(g) for g in popular)
    used.update(g["slug"] for g in popular)

    shelves = []
    for cat in HOME_SHELVES:
        games = groups.get(cat, [])
        url = S.category_url(cat)
        if not games or not url:
            continue
        ordered = sorted((g for g in games if g.get("thumbnail") and g["slug"] not in used),
                         key=lambda g: (S.source_rank(g), games.index(g)))
        picks = ordered[:18]
        used.update(g["slug"] for g in picks)
        shelves.append(S.shelf(esc(S.pretty_genre(cat)), "".join(S.card(g, show_meta=False) for g in picks),
                               more_href=url, count=f"{len(games)} games", dot=S.genre_color(cat)))

    for pos, ad in ((3, f'<div class="shelf--ad">{S.ad_native("ad--panel")}</div>'),
                    (8, f'<div class="shelf--ad">{S.ad_leader(mobile="rect")}</div>')):
        if len(shelves) > pos:
            shelves.insert(pos, ad)

    genre_tiles = "".join(
        f'<a class="genre-tile" href="{url}">{S.icon(S.genre_icon(cat))}<span class="genre-tile__name">{esc(S.pretty_genre(cat))}</span><span class="genre-tile__count">{n}</span></a>'
        for cat, n, url in sorted(genre_pages, key=lambda x: S.pretty_genre(x[0]).lower())
    )

    title = "Pixelsprout — Play. Grow. Explore."
    description = "Pixelsprout is a free browser gaming library with thousands of games across every genre. No installs, no accounts — just click and play."
    meta_extra = "\n".join([
        '<meta name="p:domain_verify" content="119e6733e3c5887bb3f24d440ab498fa"/>',
        '<meta property="og:type" content="website">',
        '<meta property="og:url" content="https://playpixelsprout.com/">',
        '<meta property="og:title" content="Pixelsprout - Play. Grow. Explore.">',
        '<meta property="og:description" content="Pixelsprout is a free browser gaming library with thousands of games across every genre. No installs, no accounts -- just click and play.">',
        '<meta property="og:image" content="https://playpixelsprout.com/assets/og-banner.jpg">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="971">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:title" content="Pixelsprout - Play. Grow. Explore.">',
        '<meta name="twitter:description" content="Free browser gaming library with thousands of games. No installs, no accounts.">',
        '<meta name="twitter:image" content="https://playpixelsprout.com/assets/og-banner.jpg">',
    ])
    website_ld = json.dumps({
        "@context": "https://schema.org", "@type": "WebSite", "name": "Pixelsprout", "url": f"{DOMAIN}/",
    })
    head = S.head(esc(title), esc(description), meta_extra=meta_extra, jsonld=[website_ld], preload_image=preload,
                  head_extra='<link rel="preconnect" href="https://img.gamepix.com">\n<link rel="preconnect" href="https://img.gamemonetize.com">')

    continue_shelf = S.shelf("Continue playing", "", section_id="continue-playing", hidden=True,
                             track_id="continue-playing-track")
    popular_shelf = S.shelf("Popular now", popular_cards, section_id="popular-now")

    main = f"""<div class="home-intro">
<h1>Free browser games</h1>
<p>{total:,} games across {len(genre_pages)} genres. Nothing to install, no account needed.</p>
</div>
{hero_html}
{continue_shelf}
{popular_shelf}
{''.join(shelves)}
<section class="shelf" id="all-genres" aria-labelledby="all-genres-title">
<div class="shelf__head"><h2 class="shelf__title" id="all-genres-title">Browse all genres</h2><span class="shelf__count">{len(genre_pages)} genres</span></div>
<div class="genre-grid">{genre_tiles}</div>
</section>
<div class="home-foot"><a class="btn btn--ghost" href="/all-games/">{S.icon('list', 'i i--sm')}All games A–Z</a><a class="btn btn--ghost" href="/guides/">{S.icon('book', 'i i--sm')}Game guides</a></div>"""
    return S.page(head, main, body_attrs='class="home-page" data-page="home"', active="/", total_games=total)


def render_all_games(catalog):
    games = sorted(catalog, key=lambda g: g["title"].strip().lower())
    groups = {}
    for g in games:
        first = g["title"].strip()[:1].upper()
        key = first if first.isalpha() else "#"
        groups.setdefault(key, []).append(g)
    order = (["#"] if "#" in groups else []) + sorted(k for k in groups if k != "#")
    nav = "".join(f'<a href="#letter-{"num" if k == "#" else k}">{k}</a>' for k in order)
    sections = []
    for k in order:
        anchor = "num" if k == "#" else k
        items = "".join(
            f'<li><a href="/games/{esc(g["slug"])}.html">{esc(g["title"])}</a><span>{esc(S.pretty_genre(g.get("category", "")))}</span></li>'
            for g in groups[k]
        )
        sections.append(f'<section class="az-group" id="letter-{anchor}"><h2>{k}</h2><ul class="az-list">{items}</ul></section>')
    title = "All Games A–Z - Every Free Game on Pixelsprout"
    description = f"An alphabetical list of all {len(games):,} free browser games on Pixelsprout. No downloads, no accounts."
    head = S.head(esc(title), esc(description), canonical=f"{DOMAIN}/all-games/",
                  jsonld=[json.dumps({
                      "@context": "https://schema.org", "@type": "BreadcrumbList",
                      "itemListElement": [
                          {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{DOMAIN}/"},
                          {"@type": "ListItem", "position": 2, "name": "All games A–Z", "item": f"{DOMAIN}/all-games/"},
                      ]})])
    main = f"""{S.crumbs([("Home", "/"), ("All games A–Z", None)])}
<header class="page-head">
<h1 class="page-title">All games, A–Z</h1>
<p class="page-lede">Every game on Pixelsprout in one list — {len(games):,} of them. Looking for something specific? <button class="btn btn--quiet" type="button" data-search-open>Search instead</button></p>
</header>
<nav class="az-nav" aria-label="Jump to letter">{nav}</nav>
{''.join(sections)}"""
    return S.page(head, main, body_attrs='class="az-page" data-page="all-games"', active="/all-games/", total_games=len(games))


FEATURED_GUIDES = [
    ("Getting Over It", "getting-over-it", "A hammer-climbing challenge played with the mouse. This is a fan-made browser remake.",
     [("Short video on YouTube", "https://www.youtube.com/shorts/glZERu6lgBE"), ("Reel on Facebook", "https://www.facebook.com/reel/956487844203977"), ("Carousel on Instagram", "https://www.instagram.com/p/Dd8M05Tm-lc/"), ("Post on X", "https://x.com/Playpixelsprout/status/2105534668061958589"), ("Join the conversation on Discord", "https://discord.com/channels/1554923717556183120/1554923718181126305/1555096012270469233")]),
    ("Bubble Up Endless", "bubble-up-endless", "A bubble shooter where you press and hold to aim, release to shoot, and chain combos before the red line.",
     [("Short video on YouTube", "https://youtube.com/shorts/zeVo-cKj_qE"), ("Reel on Facebook", "https://www.facebook.com/reel/1127971539689130"), ("Carousel on Instagram", "https://www.instagram.com/playpixelsprout/p/Dd-Bee5m7Fe/"), ("Post on X", "https://x.com/Playpixelsprout/status/2105787341965332762")]),
    ("Dot Link Puzzle", "dot-link-puzzle-connect-the-dots", "A connect-the-dots puzzle with boards from 5x5 up to 9x9, plus undo, reset and hint buttons.",
     [("Short video on YouTube", "https://youtube.com/shorts/OR3MsgtAMQU"), ("Reel on Facebook", "https://www.facebook.com/reel/2109658733245485"), ("Carousel on Instagram", "https://www.instagram.com/playpixelsprout/p/DeAmPNtmz50/"), ("Post on X", "https://x.com/Playpixelsprout/status/2106149730463957308")]),
    ("Baba Is You", "baba-is-you", "A turn-based puzzle where you push word blocks to change the rules. This is a fan-made browser remake.", []),
    ("2048 Cube Run", "2048-cube-run", "A three-lane runner where numbered cubes merge as you run toward the finish gate.", []),
]


def _featured_guides_html():
    out = ['<section aria-labelledby="featured-guides-title"><h2 class="block__title" id="featured-guides-title">Featured guides</h2>',
           '<p class="page-lede">Written after playing each game. Every game is free in your browser, with no download.</p>']
    for name, slug, blurb, social in FEATURED_GUIDES:
        links = [("Play", f"/games/{slug}.html"), ("Tips", f"/guides/{slug}-tips/"), ("Controls", f"/guides/{slug}-controls/"),
                 ("Beginner guide", f"/guides/{slug}-beginner-guide/"), ("FAQ", f"/guides/{slug}-faq/"), ("Similar games", f"/guides/games-like-{slug}/")]
        li = ' &middot; '.join(f'<a href="{h}">{esc(t)}</a>' for t, h in links)
        so = ''
        if social:
            so = '<p>' + ' &middot; '.join(f'<a href="{h}" rel="noopener" target="_blank">{esc(t)}</a>' for t, h in social) + '</p>'
        out.append(f'<h3>{esc(name)}</h3><p>{esc(blurb)}</p><p>{li}</p>{so}')
    out.append('</section>')
    return ''.join(out)


def render_guides_hub(total_games=None):
    title = "Game Guides - Tips, Controls & FAQs | Pixelsprout"
    description = "Tips, controls, beginner guides, and FAQs for every game on Pixelsprout."
    head = S.head(esc(title), esc(description), canonical=f"{DOMAIN}/guides/")
    main = f"""{S.crumbs([("Home", "/"), ("Guides", None)])}
<header class="page-head">
<p class="eyebrow">Read</p>
<h1 class="page-title">Game guides</h1>
<p class="page-lede">Tips, controls, beginner guides and FAQs for the games on Pixelsprout.</p>
</header>
{_featured_guides_html()}
<h2 class="block__title">All game guides</h2>
<div class="catalog-bar"><label class="field"><span class="visually-hidden">Filter guides</span>{S.icon('search')}<input id="guides-search" type="search" placeholder="Find a game's guides" autocomplete="off"></label><span class="catalog-bar__count" id="guides-count"></span></div>
<ul class="az-list" id="guides-list"></ul>
<script>
fetch('/guides-index.json')
  .then(r => r.json())
  .then(data => {{
    const entries = Object.keys(data).map(slug => ({{ slug, pages: data[slug], name: slug.replace(/-/g, ' ') }}))
      .sort((a, b) => a.name.localeCompare(b.name));
    const list = document.getElementById('guides-list');
    const count = document.getElementById('guides-count');
    const search = document.getElementById('guides-search');
    function render(filter) {{
      const f = (filter || '').toLowerCase().trim();
      const shown = entries.filter(e => e.name.includes(f));
      list.textContent = '';
      shown.slice(0, 600).forEach(e => {{
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.href = e.pages.tips || Object.values(e.pages)[0];
        a.textContent = e.name.replace(/\\b\\w/g, c => c.toUpperCase());
        const s = document.createElement('span');
        s.textContent = Object.keys(e.pages).length + ' guides';
        li.append(a, s);
        list.appendChild(li);
      }});
      count.textContent = shown.length.toLocaleString() + ' games';
    }}
    render('');
    search.addEventListener('input', () => render(search.value));
  }})
  .catch(() => {{
    document.getElementById('guides-list').textContent = 'Guides are being generated - check back soon.';
  }});
</script>"""
    return S.page(head, main, body_attrs='class="guides-hub" data-page="guides"', active="/guides/", total_games=total_games)


# ---------------------------------------------------------------------------
# Writers used by the generator scripts and migrate-ui.py
# ---------------------------------------------------------------------------

MIN_CATEGORY_GAMES = 15


def _write(path, content):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def build_category_pages(catalog, write=True, only=None):
    """One page per category with 15+ games (same rule as before); returns {path: html}."""
    position = {g["slug"]: i for i, g in enumerate(catalog)}
    raw_counts = {}
    for g in catalog:
        raw_counts[g.get("category", "")] = raw_counts.get(g.get("category", ""), 0) + 1
    qualifying = [c for c, n in raw_counts.items() if c and n >= MIN_CATEGORY_GAMES]
    pages = {}
    all_categories = []
    for c in qualifying:
        members = [g for g in catalog if g.get("category") == c or
                   (S.primary_category(g.get("category", "")) == c and g.get("category") != c)]
        all_categories.append((c, len(members)))
    all_categories.sort(key=lambda x: -x[1])
    for c, _ in all_categories:
        if only and S.slugify(c) not in only:
            continue
        members = [g for g in catalog if g.get("category") == c or
                   (S.primary_category(g.get("category", "")) == c and g.get("category") != c)]
        members.sort(key=lambda g: (S.source_rank(g), not g.get("thumbnail"), position[g["slug"]]))
        html_doc = render_category_page(c, members, all_categories, total_games=len(catalog), newness=position)
        path = os.path.join(S.ROOT, S.slugify(c), "index.html")
        pages[path] = html_doc
        if write:
            _write(path, html_doc)
    return pages


def _load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return default


def build_home(catalog, write=True):
    featured = _load_json(os.path.join(S.ROOT, "featured.json"), {}).get("games", [])
    popular = _load_json(os.path.join(S.ROOT, "popular-games.json"), {}).get("games", [])
    pages = {
        os.path.join(S.ROOT, "index.html"): render_home(catalog, featured, popular),
        os.path.join(S.ROOT, "all-games", "index.html"): render_all_games(catalog),
    }
    if write:
        for path, html_doc in pages.items():
            _write(path, html_doc)
    return pages


def refresh_game_page(slug, catalog, guides_index, write=True):
    """Re-render one existing game page (e.g. after its guides were generated)."""
    path = os.path.join(S.ROOT, "games", f"{slug}.html")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        doc = f.read()
    fields = extract_game_page(doc, slug)
    if not fields:
        return None
    html_doc = render_game_page(fields, catalog, guides=guides_index.get(slug), total_games=len(catalog))
    if write:
        _write(path, html_doc)
    return html_doc
