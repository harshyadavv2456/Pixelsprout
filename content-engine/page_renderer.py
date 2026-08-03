"""
Renders guide pages and collection pages into the same site-wide template
used everywhere else (game-shell layout, real ad slots, real GA4 tag,
canonical/OG/schema metadata) - these are never meant to look or behave
like a bolted-on "blog," just more pages of the same site.
"""

ADSENSE_CLIENT = "ca-pub-8466016918717424"
AD_SLOT_BANNER = "4936643192"
AD_SLOT_RIBBON = "1457517471"
GA_ID = "G-VTNJRV4WG8"
SITE = "https://playpixelsprout.com"


def _head(title, description, canonical_path, og_image, schema_blocks):
    schema_html = "\n".join(
        f'<script type="application/ld+json">{s}</script>' for s in schema_blocks
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="canonical" href="{SITE}{canonical_path}">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="stylesheet" href="/styles.css">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>
<meta property="og:type" content="article">
<meta property="og:url" content="{SITE}{canonical_path}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{og_image}">
{schema_html}
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA_ID}');
</script>
<script defer src="/pixelsprout-features.js"></script>
</head>
"""


def _breadcrumb(items):
    """items: list of (label, href_or_None_for_current)"""
    parts = []
    for label, href in items:
        if href:
            parts.append(f'<a href="{href}" style="color:var(--teal);text-decoration:none;">{label}</a>')
        else:
            parts.append(label)
    return " / ".join(parts)


def _related_grid(games, base_prefix):
    cards = []
    for g in games:
        cards.append(
            f'<a class="similar-card" href="{base_prefix}games/{g["slug"]}.html">'
            f'<img src="{g["thumbnail"]}" alt="" loading="lazy"><span>{g["title"]}</span></a>'
        )
    return "\n".join(cards)


def render_guide_page(page_type, game, content, related_games, sibling_guides):
    """
    page_type: "tips" | "controls" | "beginner-guide" | "similar"
    content: dict from either Groq or fallback_content, shape depends on page_type
    related_games: list of similar catalog games (internal linking)
    sibling_guides: dict of {page_type: url} for this same game's other 3 guide pages
    """
    title_map = {
        "tips": f"{game['title']} - Tips, Tricks & How to Get a High Score",
        "controls": f"{game['title']} Controls - How to Play (Desktop & Mobile)",
        "beginner-guide": f"{game['title']} Beginner's Guide - How to Get Started",
        "similar": f"Games Like {game['title']} - {game['category']} Games to Try Next",
    }
    desc_map = {
        "tips": f"Tips and strategies to improve at {game['title']} and get a higher score, from the basics to more advanced play.",
        "controls": f"Full control scheme for {game['title']} on both desktop and mobile - keyboard, mouse, and touch.",
        "beginner-guide": f"New to {game['title']}? Here's everything to know before your first playthrough.",
        "similar": f"Enjoyed {game['title']}? Here are more {game['category'].lower()} games to play free on Pixelsprout.",
    }
    slug_suffix_map = {
        "tips": f"{game['slug']}-tips",
        "controls": f"{game['slug']}-controls",
        "beginner-guide": f"{game['slug']}-beginner-guide",
        "similar": f"games-like-{game['slug']}",
    }
    slug_path = slug_suffix_map[page_type]
    canonical_path = f"/guides/{slug_path}/"
    title = title_map[page_type]
    description = desc_map[page_type]

    crumb_label_map = {
        "tips": "Tips",
        "controls": "Controls",
        "beginner-guide": "Beginner's Guide",
        "similar": "Games Like This",
    }

    schema = [
        (
            '{"@context":"https://schema.org","@type":"Article","headline":"%s",'
            '"about":{"@type":"VideoGame","name":"%s"},"image":"%s"}'
        ) % (title.replace('"', "'"), game["title"].replace('"', "'"), game["thumbnail"]),
        (
            '{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
            '{"@type":"ListItem","position":1,"name":"Home","item":"%s/"},'
            '{"@type":"ListItem","position":2,"name":"Guides","item":"%s/guides/"},'
            '{"@type":"ListItem","position":3,"name":"%s","item":"%s%s"}]}'
        ) % (SITE, SITE, title.replace('"', "'"), SITE, canonical_path),
    ]

    head = _head(title + " | Pixelsprout", description, canonical_path, game["thumbnail"], schema)
    crumb = _breadcrumb([
        ("Home", "/index.html"),
        ("Guides", "/guides/"),
        (game["title"], f"/games/{game['slug']}.html"),
        (crumb_label_map[page_type], None),
    ])

    body_html = _render_body_for_type(page_type, game, content)

    sibling_labels = {
        "tips": "Tips & Strategy",
        "controls": "Controls",
        "beginner-guide": "Beginner's Guide",
        "similar": "Games Like This",
    }
    other_guides_links = "\n".join(
        f'<a class="similar-card" href="{url}"><span>{sibling_labels[key]}</span></a>'
        for key, url in sibling_guides.items() if key != page_type
    )

    return f"""{head}
<body data-tool-slug="guide-{page_type}">
<div class="game-shell">
  <div class="breadcrumb" style="font-family:'IBM Plex Mono',monospace;font-size:12px;color:var(--muted);margin-bottom:8px;">{crumb}</div>
  <a class="back-link" href="/games/{game['slug']}.html">&larr; back to {game['title']}</a>
  <h1 class="game-title">{title}</h1>
  <div class="game-meta">Guide &middot; {game['category']}</div>

  <div class="ad-slot ad-slot-banner">
    <ins class="adsbygoogle" style="display:block" data-ad-client="{ADSENSE_CLIENT}" data-ad-slot="{AD_SLOT_BANNER}" data-ad-format="auto" data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
  </div>

  <div class="game-board-frame">
    <article class="guide-body" style="max-width:760px;margin:0 auto;color:var(--muted,#8a93b8);font-family:system-ui,sans-serif;font-size:15px;line-height:1.75;">
      {body_html}
    </article>

    <div class="ad-slot ad-slot-ribbon">
      <ins class="adsbygoogle" style="display:block" data-ad-client="{ADSENSE_CLIENT}" data-ad-slot="{AD_SLOT_RIBBON}" data-ad-format="auto" data-full-width-responsive="true"></ins>
      <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
    </div>

    <div class="similar-games">
      <h3 class="similar-games-title">More about {game['title']}</h3>
      <div class="similar-games-grid">{other_guides_links}</div>
    </div>

    <div class="similar-games">
      <h3 class="similar-games-title">Play something similar</h3>
      <div class="similar-games-grid">{_related_grid(related_games, "/")}</div>
    </div>
  </div>
</div>
</body>
</html>
"""


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
    return ""


def render_collection_page(collection, games, content):
    display_name = collection["display_name"]
    title = f"Games Like {display_name} - Free Browser Alternatives | Pixelsprout"
    description = f"Love {display_name}? Here are the best free, browser-playable alternatives on Pixelsprout - no download needed."
    canonical_path = f"/games-like/{collection['slug']}/"

    items_json = ",".join(
        '{"@type":"ListItem","position":%d,"name":"%s","url":"%s/games/%s.html"}'
        % (i + 1, g["title"].replace('"', "'"), SITE, g["slug"])
        for i, g in enumerate(games)
    )
    schema = [
        '{"@context":"https://schema.org","@type":"ItemList","itemListElement":[%s]}' % items_json,
        (
            '{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
            '{"@type":"ListItem","position":1,"name":"Home","item":"%s/"},'
            '{"@type":"ListItem","position":2,"name":"Games Like %s","item":"%s%s"}]}'
        ) % (SITE, display_name, SITE, canonical_path),
    ]

    og_image = games[0]["thumbnail"] if games else f"{SITE}/assets/logo-icon.png"
    head = _head(title, description, canonical_path, og_image, schema)
    crumb = _breadcrumb([("Home", "/index.html"), (f"Games Like {display_name}", None)])
    grid = _related_grid(games, "/")

    return f"""{head}
<body>
<div class="game-shell">
  <div class="breadcrumb" style="font-family:'IBM Plex Mono',monospace;font-size:12px;color:var(--muted);margin-bottom:8px;">{crumb}</div>
  <a class="back-link" href="/index.html">&larr; back to Pixelsprout</a>
  <h1 class="game-title">Games Like {display_name}</h1>
  <div class="game-meta">Collection &middot; {len(games)} games</div>

  <div class="ad-slot ad-slot-banner">
    <ins class="adsbygoogle" style="display:block" data-ad-client="{ADSENSE_CLIENT}" data-ad-slot="{AD_SLOT_BANNER}" data-ad-format="auto" data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
  </div>

  <div class="game-board-frame">
    <p style="max-width:760px;margin:0 auto 20px;color:var(--muted,#8a93b8);font-family:system-ui,sans-serif;font-size:15px;line-height:1.75;">{content.get('intro','')}</p>
    <div class="similar-games-grid">{grid}</div>

    <div class="ad-slot ad-slot-ribbon">
      <ins class="adsbygoogle" style="display:block" data-ad-client="{ADSENSE_CLIENT}" data-ad-slot="{AD_SLOT_RIBBON}" data-ad-format="auto" data-full-width-responsive="true"></ins>
      <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
    </div>
  </div>
</div>
</body>
</html>
"""
