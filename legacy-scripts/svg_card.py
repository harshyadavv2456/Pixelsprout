"""
Generates a small, unique SVG "stat card" per game - title, category, and
a deterministic accent color derived from the game's slug. This is the
second image per guide page: real per-game visual content, zero API cost,
never generic/interchangeable between games (unlike a stock illustration
would be). The game's own GamePix thumbnail is the first image (used as
the hero at the top of the article and in og:image).
"""

import hashlib

# A small, deliberately on-brand palette (matches the site's dark/neon
# theme) rather than fully random colors per game.
ACCENTS = ["#7BE0D6", "#F2C94C", "#EF798A", "#6C8CFF", "#8BD17C", "#C792EA"]


def _accent_for(slug):
    h = int(hashlib.md5(slug.encode("utf-8")).hexdigest(), 16)
    return ACCENTS[h % len(ACCENTS)]


def _esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


def render_stat_card_svg(game):
    accent = _accent_for(game["slug"])
    title = _esc(game["title"])
    category = _esc(game["category"])

    return f"""<svg width="640" height="200" viewBox="0 0 640 200" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{title} - {category} game on Pixelsprout" style="width:100%;height:auto;max-width:640px;display:block;">
<rect width="640" height="200" rx="14" fill="#151a2e"/>
<rect x="0" y="0" width="8" height="200" rx="4" fill="{accent}"/>
<text x="36" y="70" font-family="'Press Start 2P', monospace" font-size="20" fill="#ffffff">{title}</text>
<text x="36" y="104" font-family="system-ui, sans-serif" font-size="15" fill="{accent}">{category} &middot; Play free on Pixelsprout</text>
<circle cx="580" cy="100" r="46" fill="none" stroke="{accent}" stroke-width="3" opacity="0.5"/>
<circle cx="580" cy="100" r="30" fill="{accent}" opacity="0.15"/>
<text x="580" y="107" font-family="'Press Start 2P', monospace" font-size="12" fill="{accent}" text-anchor="middle">PLAY</text>
<text x="36" y="160" font-family="system-ui, sans-serif" font-size="12" fill="#8a93b8">No download &middot; No account &middot; Free browser play</text>
</svg>"""
