#!/usr/bin/env python3
"""
One-time (idempotent) bulk injection of Adsterra ad units across the existing
static site. Safe to re-run - every insertion is guarded by a unique HTML
comment marker, so running this twice will never double-insert.

Does NOT touch:
  - ads.txt
  - index.html (homepage)
  - any existing AdSense <ins class="adsbygoogle"> slots or scripts
  - about.html, terms.html, or category landing pages (board/, ball/, etc.)

Placement:
  - games/*.html          -> Adsterra 300x250 banner + 728x90 banner +
                              Popunder script (before </head>)
  - guides/*/index.html   -> Adsterra 728x90 banner (top) + 300x250 banner
                              (bottom). No popunder on guide/blog pages.
  - games-like/*/index.html -> same as guides (collection pages).
"""

import glob
import re

MARK_300 = "<!-- ADSTERRA-300x250 -->"
MARK_728 = "<!-- ADSTERRA-728x90 -->"
MARK_POP = "<!-- ADSTERRA-POPUNDER -->"

BANNER_300 = f"""{MARK_300}
<div class="adsterra-slot adsterra-300x250" style="margin:16px auto;text-align:center;max-width:300px;">
<script>
atOptions = {{
  'key' : '9de242ffc7b556a74ae29033348b18bd',
  'format' : 'iframe',
  'height' : 250,
  'width' : 300,
  'params' : {{}}
}};
</script>
<script src="https://www.highperformanceformat.com/9de242ffc7b556a74ae29033348b18bd/invoke.js"></script>
</div>
"""

BANNER_728 = f"""{MARK_728}
<div class="adsterra-slot adsterra-728x90" style="margin:16px auto;text-align:center;max-width:728px;">
<script>
atOptions = {{
  'key' : 'da5095b2daea5c6ba87d034975239610',
  'format' : 'iframe',
  'height' : 90,
  'width' : 728,
  'params' : {{}}
}};
</script>
<script src="https://www.highperformanceformat.com/da5095b2daea5c6ba87d034975239610/invoke.js"></script>
</div>
"""

POPUNDER = f'{MARK_POP}\n<script src="https://pl30769900.effectivecpmnetwork.com/51/6e/a8/516ea83fbec98f4dc14cea105216b6c1.js"></script>\n'


def inject_game_page(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    if MARK_300 in html and MARK_728 in html and MARK_POP in html:
        return False  # already done

    changed = False

    # Popunder: right before </head>
    if MARK_POP not in html and "</head>" in html:
        html = html.replace("</head>", POPUNDER + "</head>", 1)
        changed = True

    # 300x250: right after the embed frame / fullscreen button, before the
    # existing AdSense ribbon slot (inside game-board-frame).
    if MARK_300 not in html:
        anchor = re.search(r'<div class="ad-slot ad-slot-ribbon">', html)
        if anchor:
            idx = anchor.start()
            html = html[:idx] + BANNER_300 + "\n" + html[idx:]
            changed = True

    # 728x90: right after the existing AdSense ribbon slot closes, before
    # "similar games" section.
    if MARK_728 not in html:
        anchor = re.search(r'<div class="similar-games">', html)
        if anchor:
            idx = anchor.start()
            html = html[:idx] + BANNER_728 + "\n" + html[idx:]
            changed = True

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
    return changed


def inject_guide_or_collection_page(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    if MARK_300 in html and MARK_728 in html:
        return False  # already done

    changed = False

    # 728x90: right after the existing top AdSense banner slot closes.
    if MARK_728 not in html:
        anchor = re.search(r'<div class="ad-slot ad-slot-banner">.*?</div>\s*', html, re.DOTALL)
        if anchor:
            idx = anchor.end()
            html = html[:idx] + BANNER_728 + "\n" + html[idx:]
            changed = True

    # 300x250: right before the existing bottom AdSense ribbon slot.
    if MARK_300 not in html:
        anchor = re.search(r'<div class="ad-slot ad-slot-ribbon">', html)
        if anchor:
            idx = anchor.start()
            html = html[:idx] + BANNER_300 + "\n" + html[idx:]
            changed = True

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
    return changed


def main():
    game_files = sorted(glob.glob("games/*.html"))
    guide_files = sorted(glob.glob("guides/*/index.html"))
    collection_files = sorted(glob.glob("games-like/*/index.html"))

    g_changed = sum(1 for p in game_files if inject_game_page(p))
    gu_changed = sum(1 for p in guide_files if inject_guide_or_collection_page(p))
    c_changed = sum(1 for p in collection_files if inject_guide_or_collection_page(p))

    print(f"games/*.html:            {g_changed}/{len(game_files)} updated")
    print(f"guides/*/index.html:     {gu_changed}/{len(guide_files)} updated")
    print(f"games-like/*/index.html: {c_changed}/{len(collection_files)} updated")


if __name__ == "__main__":
    main()
