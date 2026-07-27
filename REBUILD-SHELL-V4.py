#!/usr/bin/env python3
"""
Shell rebuild v3 for Pixelsprout.

v1 and v2 tried to find section boundaries by pattern-matching on HTML
content (e.g. "find the next </div>"), which is fragile — nested divs and
repeated class names caused real bugs (a duplicated Popular Picks section).

v3 fixes this at the root: it wraps the Popular Picks section in explicit,
unique HTML comment markers (<!-- POPULAR_PICKS_START/END -->) and uses
THOSE as the only boundary logic. Comments can't be confused with nested
content, so this is safe to re-run any number of times, forever, with no
risk of duplication.

Also includes all prior fixes: hero simplified to headline only, search
hides Popular Picks and shows results first, search bar has no separate
background box.
"""

import re
import sys

INDEX_FILE = "index.html"

POPULAR_PICKS_BLOCK = """<!-- POPULAR_PICKS_START -->
  <div id="popular-picks" class="category gold" data-section>
    <span class="bar"></span>
    <h2>Popular Picks</h2>
    <span class="count">Featured</span>
  </div>
  <div id="popular-picks-grid" class="grid" data-grid>
    <a class="card popular-slot" href="games/subway-princess-run.html" data-clone-from="games/subway-princess-run.html"></a>
    <a class="card popular-slot" href="games/worms-zone.html" data-clone-from="games/worms-zone.html"></a>
    <a class="card popular-slot" href="games/uno-online.html" data-clone-from="games/uno-online.html"></a>
    <a class="card popular-slot" href="games/baba-is-you.html" data-clone-from="games/baba-is-you.html"></a>
    <a class="card popular-slot" href="games/getting-over-it.html" data-clone-from="games/getting-over-it.html"></a>
    <a class="card popular-slot" href="games/suika-world.html" data-clone-from="games/suika-world.html"></a>
    <a class="card popular-slot" href="games/tank-1990.html" data-clone-from="games/tank-1990.html"></a>
    <a class="card popular-slot" href="games/ultimate-solitaire-classic.html" data-clone-from="games/ultimate-solitaire-classic.html"></a>
  </div>
<!-- POPULAR_PICKS_END -->"""


def main():
    with open(INDEX_FILE, encoding="utf-8") as f:
        html = f.read()

    # --- Strip ANY existing Popular Picks block(s), using the unambiguous
    #     comment markers if present. Removes all of them, however many. ---
    marker_pattern = re.compile(r'<!-- POPULAR_PICKS_START -->.*?<!-- POPULAR_PICKS_END -->\s*', re.DOTALL)
    html, n_removed_marked = marker_pattern.subn('', html)

    # --- Also strip any OLDER-style Popular Picks blocks that predate the
    #     comment markers (from earlier patch attempts), identified by their
    #     id, up to the next id="..." (any section) as a safe boundary. ---
    legacy_pattern = re.compile(
        r'<div id="popular-picks"[^>]*>.*?(?=<div id="|<p id="no-results")',
        re.DOTALL,
    )
    html, n_removed_legacy = legacy_pattern.subn('', html)

    total_removed = n_removed_marked + n_removed_legacy
    if total_removed:
        print(f"Removed {total_removed} existing Popular Picks block(s) before rebuilding.")

    # --- Find where the real games start: right after where Popular Picks
    #     used to be (now removed), or if this is the very first run, at
    #     the first real category section. ---
    start_match = re.search(r'<div[^>]*class="category', html)
    end_idx = html.find('<p id="no-results"')

    if not start_match or end_idx == -1:
        print("ERROR: couldn't find the game-listing boundaries. Aborting without changes to avoid data loss.")
        sys.exit(1)

    preserved_games_html = html[start_match.start():end_idx]
    total_games = len(re.findall(r'<a class="card(?!\s+popular-slot)', preserved_games_html))

    if total_games < 100:
        print(f"WARNING: only found {total_games} games in the preserved section — expected ~2,889.")
        print("Aborting without changes, since this suggests something is wrong.")
        sys.exit(1)

    print(f"Preserved {total_games} existing game cards untouched.")

    new_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" type="image/png" href="assets/logo-icon.png">
<link rel="preconnect" href="https://img.gamepix.com">
<link rel="dns-prefetch" href="https://img.gamepix.com">
<title>Pixelsprout — Play. Grow. Explore.</title>
<meta name="description" content="Pixelsprout is a free browser gaming library with thousands of games across every genre. No installs, no accounts — just click and play.">
<link rel="stylesheet" href="styles.css">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8466016918717424" crossorigin="anonymous"></script>
<script defer src="/_vercel/insights/script.js"></script>
</head>
<body>

<button id="sidebar-toggle" class="sidebar-toggle" aria-label="Toggle genre menu">☰</button>

<aside class="sidebar" id="sidebar">
  <div class="sidebar-title">Genres</div>
  <nav class="sidebar-nav">
    <a href="#" class="sidebar-link active" data-filter="all">All Games</a>
    <a href="#puzzle" class="sidebar-link">Puzzle</a>
    <a href="#arcade" class="sidebar-link">Arcade</a>
    <a href="#strategy" class="sidebar-link">Strategy</a>
    <a href="#simulation" class="sidebar-link">Simulation</a>
    <a href="#hidden-object" class="sidebar-link">Hidden-Object</a>
    <a href="#match-3" class="sidebar-link">Match-3</a>
    <a href="#2048" class="sidebar-link">2048</a>
    <a href="#battle" class="sidebar-link">Battle</a>
    <a href="#memory" class="sidebar-link">Memory</a>
    <a href="#kids" class="sidebar-link">Kids</a>
  </nav>
</aside>

<header class="site-header">
  <a class="logo" href="/">
    <img class="logo-mark" src="assets/logo-icon.png" alt="Pixelsprout">
    <span class="logo-word">PIXEL<span class="sprout-part">SPROUT</span></span>
  </a>
  <span class="tagline">Play · Grow · Explore</span>
</header>

<section class="hero">
  <div class="wrap hero-inner">
    <div class="hero-text">
      <h1>One tab.<br><span class="accent">Every game.</span></h1>
      <div class="hero-trending" id="hero-trending" aria-label="Randomly featured games"></div>
    </div>
    <img class="hero-logo" src="assets/logo-full.png" alt="Pixelsprout">
  </div>
</section>

<div class="marquee" aria-hidden="true">
  <div class="marquee-track" id="marquee-track"></div>
</div>

<main class="wrap">

  <div class="search-row">
    <div class="search-box">
      <svg class="search-icon" viewBox="0 0 24 24" fill="none"><circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2"/><path d="M20 20L16.5 16.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
      <input type="text" id="search" placeholder="Search games..." autocomplete="off">
    </div>
    <span id="result-count" class="result-count">{total_games} games</span>
  </div>

{POPULAR_PICKS_BLOCK}

{preserved_games_html}
  <p id="no-results" class="no-results" hidden>No games match "<span id="no-results-term"></span>". Try a different search.</p>

</main>

<footer class="site-footer">
  <span>© Pixelsprout — Play. Grow. Explore. Some games provided via GamePix.</span>
  <span><a href="privacy.html">Privacy</a> · <a href="terms.html">Terms</a></span>
</footer>

<script>
  const cards = Array.from(document.querySelectorAll('.card:not(.popular-slot)'));
  const sections = Array.from(document.querySelectorAll('[data-section]')).filter(s => s.id !== 'popular-picks');
  const grids = Array.from(document.querySelectorAll('[data-grid]')).filter(g => g.id !== 'popular-picks-grid');
  const resultCount = document.getElementById('result-count');
  const noResults = document.getElementById('no-results');
  const noResultsTerm = document.getElementById('no-results-term');
  const searchInput = document.getElementById('search');
  const popularSection = document.getElementById('popular-picks');
  const popularGrid = document.getElementById('popular-picks-grid');

  resultCount.textContent = cards.length + ' games';

  searchInput.addEventListener('input', () => {{
    const q = searchInput.value.trim().toLowerCase();
    let visible = 0;

    if (popularSection && popularGrid) {{
      popularSection.style.display = q ? 'none' : '';
      popularGrid.style.display = q ? 'none' : '';
    }}

    cards.forEach(card => {{
      const match = card.dataset.name && card.dataset.name.includes(q);
      card.style.display = match ? '' : 'none';
      if (match) visible++;
    }});
    grids.forEach((grid, i) => {{
      const anyVisible = Array.from(grid.children).some(c => c.style.display !== 'none');
      grid.style.display = anyVisible ? '' : 'none';
      if (sections[i]) sections[i].style.display = anyVisible ? '' : 'none';
    }});
    resultCount.textContent = visible + (visible === 1 ? ' game' : ' games');
    noResults.hidden = visible !== 0;
    if (visible === 0) noResultsTerm.textContent = searchInput.value.trim();
  }});

  try {{
    const track = document.getElementById('marquee-track');
    const allTitles = cards.map(c => {{
      const h3 = c.querySelector('h3');
      return h3 ? h3.textContent.toUpperCase() : '';
    }}).filter(Boolean);
    const sampleSize = Math.min(20, allTitles.length);
    const shuffled = allTitles.slice().sort(() => 0.5 - Math.random());
    const marqueeNames = shuffled.slice(0, sampleSize);
    [...marqueeNames, ...marqueeNames].forEach(n => {{
      const span = document.createElement('span');
      span.textContent = n;
      track.appendChild(span);
    }});
  }} catch (err) {{ console.error('Marquee setup failed:', err); }}

  try {{
    const trendingEl = document.getElementById('hero-trending');
    const sample = cards.slice().sort(() => 0.5 - Math.random()).slice(0, 3);
    sample.forEach((card, i) => {{
      const img = card.querySelector('img');
      const title = card.querySelector('h3');
      if (!title) return;
      const a = document.createElement('a');
      a.className = 'hero-trending-card';
      a.href = card.getAttribute('href');
      a.style.animationDelay = (i * 0.12) + 's';
      a.innerHTML = (img ? '<img src="' + img.src + '" alt="">' : '') + '<span>' + title.textContent + '</span>';
      trendingEl.appendChild(a);
    }});
  }} catch (err) {{ console.error('Hero trending setup failed:', err); }}

  try {{
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebarEl = document.getElementById('sidebar');
    sidebarToggle.addEventListener('click', (e) => {{
      e.stopPropagation();
      sidebarEl.classList.toggle('open');
    }});
    document.addEventListener('click', (e) => {{
      if (!sidebarEl.contains(e.target) && !sidebarToggle.contains(e.target)) {{
        sidebarEl.classList.remove('open');
      }}
    }});
    document.querySelectorAll('.sidebar-link').forEach(link => {{
      link.addEventListener('click', () => {{
        document.querySelectorAll('.sidebar-link').forEach(l => l.classList.remove('active'));
        link.classList.add('active');
        sidebarEl.classList.remove('open');
      }});
    }});
  }} catch (err) {{ console.error('Sidebar setup failed:', err); }}

  try {{
    document.querySelectorAll('.popular-slot').forEach(slot => {{
      const targetHref = slot.getAttribute('href');
      const realCard = Array.from(document.querySelectorAll('.card:not(.popular-slot)'))
        .find(c => c.getAttribute('href') === targetHref);
      if (realCard) {{
        slot.innerHTML = realCard.innerHTML;
        slot.dataset.name = realCard.dataset.name;
      }}
    }});
  }} catch (err) {{ console.error('Popular Picks setup failed:', err); }}
</script>

</body>
</html>
"""

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(new_html)

    print(f"Rebuilt cleanly. {total_games} games preserved, everything else rebuilt fresh.")


if __name__ == "__main__":
    main()
