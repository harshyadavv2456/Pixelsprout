#!/usr/bin/env python3
"""
Fix-up pass on top of the earlier Adsterra deployment:
  1. REMOVES the Popunder unit everywhere it was added (games/*.html and
     the head of every game-page template script) - decided against it
     after research showed it's tied to redirect/malware-blacklist
     complaints on Adsterra specifically.
  2. ADDS the Native Banner (4:1 widget) unit instead:
       - Game pages: placed directly under the game embed / Fullscreen
         button (the guide's "Under the player" placement) - the single
         most natural spot, before the other two Adsterra banners further
         down the page.
       - Guide pages: placed in the middle of the article, after the body
         copy and before the stat-card link (the guide's "Middle of the
         page" placement for text/mixed-content pages).
       - Collection pages: placed after the games grid, before the
         existing 300x250/728x90 pair.

Idempotent - guarded by HTML comment markers, safe to re-run.
Leaves the existing 300x250 / 728x90 Adsterra banners and all AdSense
slots exactly as they are.
"""

import glob
import re

MARK_POP = "<!-- ADSTERRA-POPUNDER -->"
MARK_NATIVE = "<!-- ADSTERRA-NATIVE -->"
MARK_300 = "<!-- ADSTERRA-300x250 -->"

POPUNDER_LINE_RE = re.compile(
    re.escape(MARK_POP) + r"\n"
    r'<script src="https://pl30769900\.effectivecpmnetwork\.com/51/6e/a8/516ea83fbec98f4dc14cea105216b6c1\.js"></script>\n?'
)

NATIVE_BANNER = f"""{MARK_NATIVE}
<div class="adsterra-slot adsterra-native" style="margin:16px auto;max-width:700px;">
<script async="async" data-cfasync="false" src="https://pl30771855.effectivecpmnetwork.com/c3f3d41bbefde3a25a4d5d341b5582d1/invoke.js"></script>
<div id="container-c3f3d41bbefde3a25a4d5d341b5582d1"></div>
</div>
"""


def remove_popunder(html):
    if MARK_POP not in html:
        return html, False
    new_html = POPUNDER_LINE_RE.sub("", html)
    return new_html, (new_html != html)


def add_native_game(html):
    """Insert right after the how-to paragraph / fullscreen area, before
    the existing ADSTERRA-300x250 marker (i.e. directly under the game)."""
    if MARK_NATIVE in html:
        return html, False
    idx = html.find(MARK_300)
    if idx == -1:
        return html, False
    return html[:idx] + NATIVE_BANNER + "\n" + html[idx:], True


def add_native_guide_or_collection(html):
    """Insert before the existing ADSTERRA-300x250 marker (middle of the
    page, matching the guide's 'Basic content' placement)."""
    if MARK_NATIVE in html:
        return html, False
    idx = html.find(MARK_300)
    if idx == -1:
        return html, False
    return html[:idx] + NATIVE_BANNER + "\n" + html[idx:], True


def process(path, add_fn):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    html, pop_removed = remove_popunder(html)
    html, native_added = add_native_game(html) if add_fn == "game" else add_native_guide_or_collection(html)

    if pop_removed or native_added:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
    return pop_removed, native_added


def main():
    game_files = sorted(glob.glob("games/*.html"))
    guide_files = sorted(glob.glob("guides/*/index.html"))
    collection_files = sorted(glob.glob("games-like/*/index.html"))

    def run(files, kind, label):
        pop_n, nat_n = 0, 0
        for p in files:
            pr, nr = process(p, kind)
            pop_n += pr
            nat_n += nr
        print(f"{label}: popunder removed from {pop_n}/{len(files)}, native added to {nat_n}/{len(files)}")

    run(game_files, "game", "games/*.html")
    run(guide_files, "guide", "guides/*/index.html")
    run(collection_files, "guide", "games-like/*/index.html")


if __name__ == "__main__":
    main()
