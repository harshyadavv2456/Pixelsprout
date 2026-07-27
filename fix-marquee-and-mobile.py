#!/usr/bin/env python3
"""
Second repair pass for Pixelsprout — replaces the ENTIRE inline <script>
block with a clean, correctly-ordered version, rather than patching pieces
incrementally (which risked variable-ordering bugs). This fixes:

1. Marquee speed: it was listing every game title (thousands, doubled for
   the loop) in a fixed 40-second animation, so as the catalog grew the
   ticker got faster and faster. Now it samples a small fixed number of
   titles (20) directly from the live page at load time, so its length —
   and therefore its speed — never changes no matter how big the catalog
   gets.
2. Keeps the search filter and result-count logic exactly as before,
   just correctly ordered so nothing references a variable before it
   exists.
"""

import re
import sys

INDEX_FILE = "index.html"

NEW_SCRIPT_BODY = """
  const cards = Array.from(document.querySelectorAll('.card'));
  const sections = Array.from(document.querySelectorAll('[data-section]'));
  const grids = Array.from(document.querySelectorAll('[data-grid]'));
  const resultCount = document.getElementById('result-count');
  const noResults = document.getElementById('no-results');
  const noResultsTerm = document.getElementById('no-results-term');
  const searchInput = document.getElementById('search');

  resultCount.textContent = cards.length + ' games';

  // Marquee: a small, fixed-size random sample of titles pulled straight
  // from the live page, so its length (and therefore its speed) never
  // changes no matter how large the catalog grows.
  const track = document.getElementById('marquee-track');
  const allTitles = cards.map(c => c.querySelector('h3').textContent.toUpperCase());
  const sampleSize = Math.min(20, allTitles.length);
  const shuffled = allTitles.slice().sort(() => 0.5 - Math.random());
  const marqueeNames = shuffled.slice(0, sampleSize);
  [...marqueeNames, ...marqueeNames].forEach(n => {
    const span = document.createElement('span');
    span.textContent = n;
    track.appendChild(span);
  });

  searchInput.addEventListener('input', () => {
    const q = searchInput.value.trim().toLowerCase();
    let visible = 0;

    cards.forEach(card => {
      const match = card.dataset.name.includes(q);
      card.style.display = match ? '' : 'none';
      if (match) visible++;
    });

    grids.forEach((grid, i) => {
      const anyVisible = Array.from(grid.children).some(c => c.style.display !== 'none');
      grid.style.display = anyVisible ? '' : 'none';
      sections[i].style.display = anyVisible ? '' : 'none';
    });

    resultCount.textContent = visible + (visible === 1 ? ' game' : ' games');
    if (visible === 0) {
      noResults.hidden = false;
      noResultsTerm.textContent = searchInput.value.trim();
    } else {
      noResults.hidden = true;
    }
  });
"""


def main():
    with open(INDEX_FILE, encoding="utf-8") as f:
        html = f.read()

    pattern = re.compile(r"<script>.*?</script>", re.DOTALL)
    matches = pattern.findall(html)
    if not matches:
        print("ERROR: couldn't find a <script> block to replace. Aborting without changes.")
        sys.exit(1)

    # Replace the LAST <script> block (the site's own inline logic — earlier
    # <script> tags, if any, like the AdSense snippet, are left untouched).
    last_start = html.rfind("<script>")
    last_end = html.find("</script>", last_start) + len("</script>")
    html = html[:last_start] + "<script>" + NEW_SCRIPT_BODY + "</script>" + html[last_end:]

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print("Fixed. Script rebuilt cleanly — marquee samples 20 random titles, search logic unchanged, no ordering bugs.")


if __name__ == "__main__":
    main()
