#!/usr/bin/env python3
"""
Adds Google Analytics 4 tracking to every page - index.html, category
pages, and every game page - plus two meaningful custom events:
fullscreen_click (real engagement signal) and search_used (unmet
content demand signal).

FILL IN your Measurement ID below before running.
"""

import glob
import re

# ---- FILL THIS IN ----
GA4_MEASUREMENT_ID = "G-VTNJRV4WG8"

GA4_SNIPPET = """<script async src="https://www.googletagmanager.com/gtag/js?id={id}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{id}');
</script>
"""


def patch_head(content, ga4_snippet):
    if "googletagmanager.com/gtag/js" in content:
        return content, False
    new_content = content.replace("</head>", ga4_snippet + "</head>", 1)
    return new_content, (new_content != content)


def main():
    if "PASTE_YOUR" in GA4_MEASUREMENT_ID:
        print("ERROR: fill in GA4_MEASUREMENT_ID at the top of this script first.")
        return

    snippet = GA4_SNIPPET.format(id=GA4_MEASUREMENT_ID)

    # index.html
    with open("index.html", encoding="utf-8") as f:
        content = f.read()
    content, changed = patch_head(content, snippet)
    if changed:
        # Add search_used event tracking
        search_marker = "searchInput.addEventListener('input', () => {"
        if search_marker in content and "gtag('event', 'search_used'" not in content:
            tracked = search_marker + """
    if (searchInput.value.trim().length > 2) {
      clearTimeout(window._searchTrackTimeout);
      window._searchTrackTimeout = setTimeout(() => {
        if (typeof gtag === 'function') {
          gtag('event', 'search_used', { search_term: searchInput.value.trim() });
        }
      }, 1000);
    }"""
            content = content.replace(search_marker, tracked, 1)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("index.html: GA4 + search tracking added.")
    else:
        print("index.html: already had GA4, skipped.")

    # Game pages
    patched = 0
    for path in glob.glob("games/*.html"):
        with open(path, encoding="utf-8") as f:
            content = f.read()
        content, changed = patch_head(content, snippet)
        if changed:
            if "fullscreen-btn" in content and "gtag('event', 'fullscreen_click'" not in content:
                content = content.replace(
                    "if (req) req.call(f);",
                    "if (req) req.call(f);\n      if (typeof gtag === 'function') { gtag('event', 'fullscreen_click', { game_title: document.title }); }",
                    1,
                )
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            patched += 1
    print(f"Patched {patched} game pages with GA4 + fullscreen tracking.")

    # Category pages
    cat_patched = 0
    for path in glob.glob("*/index.html"):
        if path.startswith("games/") or "/games/" in path:
            continue
        with open(path, encoding="utf-8") as f:
            content = f.read()
        content, changed = patch_head(content, snippet)
        if changed:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            cat_patched += 1
    print(f"Patched {cat_patched} category pages with GA4.")


if __name__ == "__main__":
    main()
