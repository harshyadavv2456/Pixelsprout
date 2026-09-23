#!/usr/bin/env python3
"""
Adds the shared features script (Recently Played, Favorites, Share, PWA)
to index.html and every game page. Safe, additive, single-tag insertion -
doesn't restructure anything, the JS itself handles all DOM changes at
runtime. Safe to re-run.
"""

import glob
import re

FEATURES_SCRIPT_ROOT = '<script defer src="pixelsprout-features.js"></script>\n<link rel="manifest" href="manifest.json">\n'
FEATURES_SCRIPT_GAME = '<script defer src="../pixelsprout-features.js"></script>\n<link rel="manifest" href="../manifest.json">\n'
FEATURES_SCRIPT_CATEGORY = '<script defer src="../pixelsprout-features.js"></script>\n<link rel="manifest" href="../manifest.json">\n'

PWA_REGISTER = """<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('%s').catch(() => {});
  });
}
</script>
"""


def patch_file(path, script_tag, sw_path):
    with open(path, encoding="utf-8") as f:
        content = f.read()
    if "pixelsprout-features.js" in content:
        return False
    content = content.replace("</head>", script_tag + PWA_REGISTER % sw_path + "</head>", 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return True


def main():
    if patch_file("index.html", FEATURES_SCRIPT_ROOT, "service-worker.js"):
        print("index.html: patched.")
    else:
        print("index.html: already patched, skipped.")

    game_count = 0
    for path in glob.glob("games/*.html"):
        if patch_file(path, FEATURES_SCRIPT_GAME, "../service-worker.js"):
            game_count += 1
    print(f"Patched {game_count} game pages.")

    cat_count = 0
    for path in glob.glob("*/index.html"):
        if "games/" in path:
            continue
        if patch_file(path, FEATURES_SCRIPT_CATEGORY, "../service-worker.js"):
            cat_count += 1
    print(f"Patched {cat_count} category pages.")


if __name__ == "__main__":
    main()
