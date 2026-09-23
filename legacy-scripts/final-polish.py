#!/usr/bin/env python3
"""
Fourth repair/polish pass for Pixelsprout — fixes:
1. Sidebar: turns it into a proper toggle drawer (click to open, click to
   close) instead of always-fixed-visible or entirely hidden on small screens
2. Popular Picks: replaces the placeholder icon cards with clones of the
   REAL existing cards for those same games elsewhere on the page (real
   photo thumbnails, not fake icons) — done via JS at runtime so it always
   matches whatever's actually on the page
3. Adds a preconnect hint for GamePix's image CDN, to speed up thumbnail
   loading slightly
"""

import re
import sys

INDEX_FILE = "index.html"


def main():
    with open(INDEX_FILE, encoding="utf-8") as f:
        html = f.read()

    changes = []

    # 1. Add a hamburger toggle button into the header, right before the logo
    #    (only once — check first).
    if 'id="sidebar-toggle"' not in html:
        toggle_btn = '<button id="sidebar-toggle" class="sidebar-toggle" aria-label="Toggle genre menu">☰</button>\n  '
        html = html.replace('<header class="site-header">\n', f'<header class="site-header">\n  {toggle_btn}', 1)
        changes.append("sidebar toggle button added")

    # 2. Replace the placeholder Popular Picks cards with empty slots the JS
    #    will fill with real clones. Uses the same fixed list of games
    #    originally chosen, rather than trying to regex-extract hrefs from
    #    existing markup (which is fragile when cards contain nested divs).
    POPULAR_HREFS = [
        "games/subway-princess-run.html",
        "games/worms-zone.html",
        "games/uno-online.html",
        "games/baba-is-you.html",
        "games/getting-over-it.html",
        "games/suika-world.html",
        "games/tank-1990.html",
        "games/ultimate-solitaire-classic.html",
    ]

    popular_block_pattern = re.compile(
        r'(<div id="popular-picks"[^>]*>.*?<span class="count">Featured</span>\s*</div>\s*<div class="grid" data-grid>\n)'
        r'.*?'
        r'(\n</div>\n)(?=\s*(?:<div id="|<p id="no-results"))',
        re.DOTALL,
    )
    match = popular_block_pattern.search(html)
    if match and "data-clone-from" not in html:
        new_cards = "\n".join(
            f'    <a class="card popular-slot" href="{href}" data-clone-from="{href}"></a>'
            for href in POPULAR_HREFS
        )
        html = popular_block_pattern.sub(lambda m: m.group(1) + new_cards + m.group(2), html, count=1)
        changes.append("popular picks converted to real-photo clone slots")
    elif "data-clone-from" in html:
        print("INFO: Popular Picks already converted — skipping.")
    else:
        print("WARNING: couldn't locate Popular Picks section boundaries. Leaving it untouched — check manually.")

    # 3. Add preconnect hint for the image CDN, right after <head>.
    if 'preconnect" href="https://img.gamepix.com"' not in html:
        html = html.replace(
            "<head>",
            '<head>\n<link rel="preconnect" href="https://img.gamepix.com">\n<link rel="dns-prefetch" href="https://img.gamepix.com">',
            1,
        )
        changes.append("image CDN preconnect hint added")

    # 4. Add the JS for: sidebar toggle open/close, and cloning real cards
    #    into the Popular Picks slots. Inserted before the closing </script>.
    polish_js = """
  // Sidebar: click the hamburger to open/close it as a slide-in drawer.
  const sidebarToggle = document.getElementById('sidebar-toggle');
  const sidebarEl = document.getElementById('sidebar');
  if (sidebarToggle && sidebarEl) {
    sidebarToggle.addEventListener('click', () => {
      sidebarEl.classList.toggle('open');
    });
    document.addEventListener('click', (e) => {
      if (!sidebarEl.contains(e.target) && !sidebarToggle.contains(e.target)) {
        sidebarEl.classList.remove('open');
      }
    });
    // Close it after picking a genre, since the click already navigated.
    document.querySelectorAll('.sidebar-link').forEach(link => {
      link.addEventListener('click', () => sidebarEl.classList.remove('open'));
    });
  }

  // Popular Picks: clone the REAL card (with its real photo) for each
  // featured game from wherever it actually lives on the page, instead of
  // showing a fake placeholder icon.
  document.querySelectorAll('.popular-slot').forEach(slot => {
    const targetHref = slot.dataset.cloneFrom;
    const realCard = Array.from(document.querySelectorAll('.card:not(.popular-slot)'))
      .find(c => c.getAttribute('href') === targetHref);
    if (realCard) {
      slot.innerHTML = realCard.innerHTML;
      slot.dataset.name = realCard.dataset.name;
    }
  });
"""
    last_script_close = html.rfind("</script>")
    if last_script_close != -1 and "sidebarToggle" not in html[:last_script_close]:
        html = html[:last_script_close] + polish_js + html[last_script_close:]
        changes.append("sidebar toggle + popular picks cloning JS added")

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print("Done: " + (", ".join(changes) if changes else "no changes needed — already applied"))


if __name__ == "__main__":
    main()
