"""
Renders guide pages and collection pages. Builds the page fields here, then
hands them to the site-wide templates in site_pages (repo root), so these
pages share the exact shell, cards and ad slots as every other page.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import site_pages as P  # noqa: E402
import site_shell as S  # noqa: E402

SITE = S.DOMAIN

TITLE_MAP = {
    "tips": "{t} - Tips, Tricks & How to Get a High Score",
    "controls": "{t} Controls - How to Play (Desktop & Mobile)",
    "beginner-guide": "{t} Beginner's Guide - How to Get Started",
    "similar": "Games Like {t} - {c} Games to Try Next",
    "faq": "{t} - Frequently Asked Questions",
}
DESC_MAP = {
    "tips": "Tips and strategies to improve at {t} and get a higher score, from the basics to more advanced play.",
    "controls": "Full control scheme for {t} on both desktop and mobile - keyboard, mouse, and touch.",
    "beginner-guide": "New to {t}? Here's everything to know before your first playthrough.",
    "similar": "Enjoyed {t}? Here are more {cl} games to play free on Pixelsprout.",
    "faq": "Common questions about {t} - free play, mobile support, and more.",
}
SLUG_MAP = {
    "tips": "{s}-tips",
    "controls": "{s}-controls",
    "beginner-guide": "{s}-beginner-guide",
    "similar": "games-like-{s}",
    "faq": "{s}-faq",
}
CRUMB_LABELS = {"tips": "Tips", "controls": "Controls", "beginner-guide": "Beginner's Guide", "similar": "Games Like This", "faq": "FAQ"}
SIBLING_LABELS = {"tips": "Tips & Strategy", "controls": "Controls", "beginner-guide": "Beginner's Guide", "similar": "Games Like This", "faq": "FAQ"}


def _fmt(template, game):
    return template.format(t=game["title"], c=game["category"], cl=game["category"].lower(), s=game["slug"])


def render_guide_page(page_type, game, content, related_games, sibling_guides, category_url=None):
    """
    page_type: "tips" | "controls" | "beginner-guide" | "similar" | "faq"
    content: dict from either Groq or fallback_content, shape depends on page_type
    related_games: list of similar catalog games (internal linking)
    sibling_guides: dict of {page_type: url} for this same game's other guide pages
    category_url: "/<category-slug>/" if that category page exists, else None
    """
    title = _fmt(TITLE_MAP[page_type], game)
    canonical_path = f"/guides/{_fmt(SLUG_MAP[page_type], game)}/"
    thumb = (game.get("thumbnail") or "").strip()
    safe_thumbnail = thumb or f"{SITE}/assets/logo-icon.png"

    schema = [
        json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": title,
                    "about": {"@type": "VideoGame", "name": game["title"]}, "image": safe_thumbnail}),
        json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Guides", "item": f"{SITE}/guides/"},
            {"@type": "ListItem", "position": 3, "name": title, "item": f"{SITE}{canonical_path}"},
        ]}),
    ]
    if page_type == "faq" and content.get("faqs"):
        schema.append(json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q["question"], "acceptedAnswer": {"@type": "Answer", "text": q["answer"]}}
            for q in content["faqs"]
        ]}))

    crumbs = [("Home", "/"), ("Guides", "/guides/")]
    if category_url:
        crumbs.append((S.esc(game["category"]), category_url))
    crumbs.append((S.esc(game["title"]), f"/games/{game['slug']}.html"))
    crumbs.append((CRUMB_LABELS[page_type], None))

    body = _render_body_for_type(page_type, game, content)
    if category_url:
        body += f'\n<p><a href="{category_url}">Browse more {S.esc(game["category"])} games &rarr;</a></p>'

    og = "\n".join([
        '<meta property="og:type" content="article">',
        f'<meta property="og:url" content="{SITE}{canonical_path}">',
        f'<meta property="og:title" content="{S.esc(title)} | Pixelsprout">',
        f'<meta property="og:description" content="{S.esc(_fmt(DESC_MAP[page_type], game))}">',
        f'<meta property="og:image" content="{S.esc(safe_thumbnail)}">',
    ])

    fields = {
        "title_tag": S.esc(title + " | Pixelsprout"),
        "meta_desc": S.esc(_fmt(DESC_MAP[page_type], game)),
        "canonical": f"{SITE}{canonical_path}",
        "og": og,
        "jsonld": schema,
        "crumbs": crumbs,
        "h1": S.esc(title),
        "eyebrow": f"Guide &middot; {S.esc(game['category'])}",
        "game_slug": game["slug"],
        "game_title": game["title"],
        "genre": game["category"],
        "thumbnail": thumb,
        "body": body,
        "siblings": [(url, SIBLING_LABELS[key]) for key, url in sibling_guides.items() if key != page_type],
        "related": [{"slug": g["slug"], "title": g["title"], "thumbnail": (g.get("thumbnail") or "").strip()} for g in related_games],
    }
    return P.render_guide_page(fields)


def _render_body_for_type(page_type, game, content):
    if page_type == "tips":
        tips_html = "\n".join(f"<li>{t}</li>" for t in content.get("tips", []))
        return f"""<p>{content.get('intro','')}</p>
<ol>{tips_html}</ol>
<p>{content.get('conclusion','')}</p>"""
    if page_type == "controls":
        return f"""<p>{content.get('intro','')}</p>
<h2>Desktop controls</h2>
<p>{content.get('desktop','')}</p>
<h2>Mobile controls</h2>
<p>{content.get('mobile','')}</p>
<h2>Tips</h2>
<ul>{"".join(f"<li>{t}</li>" for t in content.get('tips', []))}</ul>"""
    if page_type == "beginner-guide":
        steps_html = "\n".join(f"<li>{s}</li>" for s in content.get("first_steps", []))
        return f"""<p>{content.get('intro','')}</p>
<h2>What is {game['title']}?</h2>
<p>{content.get('what_it_is','')}</p>
<h2>First steps</h2>
<ol>{steps_html}</ol>
<h2>Who it's for</h2>
<p>{content.get('who_its_for','')}</p>"""
    if page_type == "similar":
        return f"<p>{content.get('intro','')}</p>"
    if page_type == "faq":
        faqs = content.get("faqs", [])
        return "\n".join(f"<h2>{q['question']}</h2>\n<p>{q['answer']}</p>" for q in faqs)
    return ""


def render_collection_page(collection, games, content):
    display_name = collection["display_name"]
    if collection.get("kind", "versus") == "best":
        title = f"Best {display_name} - Free to Play | Pixelsprout"
        description = f"The best {display_name.lower()} on Pixelsprout, free to play in your browser - no download needed."
        h1 = f"Best {display_name}"
    else:
        title = f"Games Like {display_name} - Free Browser Alternatives | Pixelsprout"
        description = f"Love {display_name}? Here are the best free, browser-playable alternatives on Pixelsprout - no download needed."
        h1 = f"Games Like {display_name}"
    canonical_path = f"/games-like/{collection['slug']}/"
    schema = [
        json.dumps({"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": g["title"], "url": f"{SITE}/games/{g['slug']}.html"}
            for i, g in enumerate(games)
        ]}),
        json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": h1, "item": f"{SITE}{canonical_path}"},
        ]}),
    ]
    og_image = next((g["thumbnail"] for g in games if (g.get("thumbnail") or "").strip()), f"{SITE}/assets/logo-icon.png")
    og = "\n".join([
        '<meta property="og:type" content="article">',
        f'<meta property="og:url" content="{SITE}{canonical_path}">',
        f'<meta property="og:title" content="{S.esc(title)}">',
        f'<meta property="og:description" content="{S.esc(description)}">',
        f'<meta property="og:image" content="{S.esc(og_image)}">',
    ])
    fields = {
        "title_tag": S.esc(title),
        "meta_desc": S.esc(description),
        "canonical": f"{SITE}{canonical_path}",
        "og": og,
        "jsonld": schema,
        "h1": S.esc(h1),
        "intro": content.get("intro", ""),
        "games": [{"slug": g["slug"], "title": g["title"], "thumbnail": (g.get("thumbnail") or "").strip()} for g in games],
    }
    by_slug = {g["slug"]: g for g in games}
    return P.render_collection_page(fields, by_slug)
