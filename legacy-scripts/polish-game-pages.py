#!/usr/bin/env python3
"""
Patches every embedded game page:
1. Removes "hosted via GamePix" from the visible page (the game-meta line
   and the "Game provided via GamePix" footer line) — GamePix's own terms
   only require keeping their ads inside the embedded game itself, not a
   visible attribution label on your page. A small one-time mention is
   instead added to the SITE'S footer (index.html) as a good-faith gesture,
   not repeated on every game page.
2. Adds a lightweight "You might also like" recommendations row, powered by
   games-index.json (a small file, not the full homepage) so this doesn't
   add meaningful load weight to each game page.

Safe to re-run: skips files already patched.
"""

import glob
import os
import re

SIMILAR_GAMES_BLOCK_TEMPLATE = """
    <div class="similar-games">
      <h3 class="similar-games-title">You might also like</h3>
      <div class="similar-games-grid" id="similar-games-grid"></div>
    </div>
    <script>
      fetch('../games-index.json')
        .then(r => r.json())
        .then(games => {{
          const currentSlug = '{slug}';
          const currentCategory = '{category}';
          let matches = games.filter(g => g.category === currentCategory && g.slug !== currentSlug);
          matches = matches.sort(() => 0.5 - Math.random());
          if (matches.length < 4) {{
            const others = games.filter(g => g.slug !== currentSlug && !matches.some(m => m.slug === g.slug));
            matches = matches.concat(others.sort(() => 0.5 - Math.random()).slice(0, 4 - matches.length));
          }}
          matches = matches.slice(0, 4);
          const grid = document.getElementById('similar-games-grid');
          matches.forEach(g => {{
            const a = document.createElement('a');
            a.className = 'similar-card';
            a.href = g.slug + '.html';
            a.innerHTML = '<img src="' + g.thumbnail + '" alt="" loading="lazy"><span>' + g.title + '</span>';
            grid.appendChild(a);
          }});
        }})
        .catch(() => {{}});
    </script>
"""


def main():
    files = glob.glob("games/*.html")
    patched = 0
    skipped_not_embed = 0
    skipped_already_done = 0

    for path in files:
        with open(path, encoding="utf-8") as f:
            content = f.read()

        if "embed-frame-wrap" not in content:
            skipped_not_embed += 1
            continue

        if "similar-games-grid" in content:
            skipped_already_done += 1
            continue

        slug = os.path.splitext(os.path.basename(path))[0]

        # Extract category before we remove the "hosted via GamePix" text
        cat_match = re.search(r'<div class="game-meta">([^·<]+)', content)
        category = cat_match.group(1).strip() if cat_match else "Arcade"

        # Remove "hosted via GamePix" from the visible meta line
        content = re.sub(
            r'(<div class="game-meta">[^<]+?)\s*·\s*hosted via GamePix(</div>)',
            r'\1\2',
            content,
        )

        # Remove the per-page "Game provided via GamePix" line
        content = re.sub(
            r'\s*<p class="source-note">Game provided via GamePix</p>\n?',
            '\n',
            content,
        )

        # Insert similar games block right before the closing </div></div>
        # of the game-board-frame / game-shell
        similar_block = SIMILAR_GAMES_BLOCK_TEMPLATE.format(slug=slug, category=category)
        marker = "  </div>\n</div>"
        if marker in content:
            content = content.replace(marker, similar_block + "  </div>\n</div>", 1)
        else:
            # Fallback: insert right before </body>
            content = content.replace("</body>", similar_block + "</body>", 1)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        patched += 1

    print(f"Patched: {patched}")
    print(f"Skipped (not an embed page, e.g. your 8 original games): {skipped_not_embed}")
    print(f"Skipped (already patched): {skipped_already_done}")


if __name__ == "__main__":
    main()
