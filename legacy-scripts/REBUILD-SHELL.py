#!/usr/bin/env python3
"""
Full shell rebuild for Pixelsprout.

This does NOT touch your actual game listings — the ~2,889 game cards and
their category sections are extracted as-is and reinserted untouched.

Everything AROUND that content — head, header, sidebar, hero, search bar,
ticker, footer, and all JavaScript — is rebuilt fresh as one clean,
internally-consistent block, replacing whatever combination of previous
patches is currently in place. This avoids relying on several small patches
having all applied correctly in the right order.
"""

import re
import sys

INDEX_FILE = "index.html"


def main():
    with open(INDEX_FILE, encoding="utf-8") as f:
        html = f.read()

    # --- Extract the preserved game-listing content ---
    start_match = re.search(r'<div[^>]*class="category', html)
    end_idx = html.find('<p id="no-results"')

    if not start_match or end_idx == -1:
        print("ERROR: couldn't find the game-listing boundaries. Aborting without changes to avoid data loss.")
        sys.exit(1)

    preserved_games_html = html[start_match.start():end_idx]
    total_games = len(re.findall(r'<a class="card', preserved_games_html))

    if total_games < 100:
        print(f"WARNING: only found {total_games} games in the preserved section — expected ~2,889.")
        print("Aborting without changes, since this suggests the boundaries were detected wrong.")
        print("If you're SURE this is correct (e.g. testing on a small file), remove this check and rerun.")
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
      <p>Pixelsprout is a free browser gaming library with thousands of titles across every genre — puzzle, arcade, strategy, simulation, and more. No downloads, no sign-ups. Pick a genre from the menu, or search for something specific, and you're playing in seconds.</p>
      <div class="hero-stats">
        <div><strong id="game-count">{total_games}</strong>games live</div>
      </div>
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

  <div id="popular-picks" class="category gold" data-section>
    <span class="bar"></span>
    <h2>Popular Picks</h2>
    <span class="count">Featured</span>
  </div>
  <div class="grid" data-grid>
    <a class="card popular-slot" href="games/subway-princess-run.html" data-clone-from="games/subway-princess-run.html"></a>
    <a class="card popular-slot" href="games/worms-zone.html" data-clone-from="games/worms-zone.html"></a>
    <a class="card popular-slot" href="games/uno-online.html" data-clone-from="games/uno-online.html"></a>
    <a class="card popular-slot" href="games/baba-is-you.html" data-clone-from="games/baba-is-you.html"></a>
    <a class="card popular-slot" href="games/getting-over-it.html" data-clone-from="games/getting-over-it.html"></a>
    <a class="card popular-slot" href="games/suika-world.html" data-clone-from="games/suika-world.html"></a>
    <a class="card popular-slot" href="games/tank-1990.html" data-clone-from="games/tank-1990.html"></a>
    <a class="card popular-slot" href="games/ultimate-solitaire-classic.html" data-clone-from="games/ultimate-solitaire-classic.html"></a>
  </div>

{preserved_games_html}
  <p id="no-results" class="no-results" hidden>No games match "<span id="no-results-term"></span>". Try a different search.</p>

</main>

<footer class="site-footer">
  <span>© Pixelsprout — Play. Grow. Explore.</span>
  <span><a href="privacy.html">Privacy</a> · <a href="terms.html">Terms</a></span>
</footer>

<script>
  const cards = Array.from(document.querySelectorAll('.card:not(.popular-slot)'));
  const sections = Array.from(document.querySelectorAll('[data-section]'));
  const grids = Array.from(document.querySelectorAll('[data-grid]'));
  const resultCount = document.getElementById('result-count');
  const noResults = document.getElementById('no-results');
  const noResultsTerm = document.getElementById('no-results-term');
  const searchInput = document.getElementById('search');

  resultCount.textContent = cards.length + ' games';

  searchInput.addEventListener('input', () => {{
    const q = searchInput.value.trim().toLowerCase();
    let visible = 0;
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
