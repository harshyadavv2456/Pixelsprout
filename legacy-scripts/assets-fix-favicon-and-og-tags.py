#!/usr/bin/env python3
"""
Fixes two real issues:

1. Favicon showing as a dull generated "P" circle instead of your actual
   logo -- root cause: your favicon source image wasn't square (870x630),
   and there was no favicon.ico at the site root, which is what browsers'
   internal UI (Chrome's quick-access tiles, bookmarks bar, etc.) actually
   fetches directly, regardless of any <link> tag in your HTML. Fixed by
   generating a proper square favicon.ico plus explicit PNG sizes, and
   linking all of them correctly.

2. No image when sharing your link (WhatsApp, etc.) -- root cause: no
   Open Graph / Twitter Card meta tags existed at all, only <title> and
   <meta name="description">, which is why text showed but no image did.
   Fixed by adding og:image pointing to your own banner design.

Run this once against your live index.html. Also lightly patches every
game page's favicon links for consistency (quick, safe, no other changes).
"""

import glob
import re

DOMAIN = "https://playpixelsprout.com"

FAVICON_LINKS_ROOT = """<link rel="icon" href="favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="assets/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="assets/apple-touch-icon.png">"""

FAVICON_LINKS_GAME_PAGE = """<link rel="icon" href="../favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="../assets/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="../assets/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="../assets/apple-touch-icon.png">"""

OG_TAGS = """<meta property="og:type" content="website">
<meta property="og:url" content="https://playpixelsprout.com/">
<meta property="og:title" content="Pixelsprout - Play. Grow. Explore.">
<meta property="og:description" content="Pixelsprout is a free browser gaming library with thousands of games across every genre. No installs, no accounts -- just click and play.">
<meta property="og:image" content="https://playpixelsprout.com/assets/og-banner.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="971">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Pixelsprout - Play. Grow. Explore.">
<meta name="twitter:description" content="Free browser gaming library with thousands of games. No installs, no accounts.">
<meta name="twitter:image" content="https://playpixelsprout.com/assets/og-banner.jpg">"""


def fix_index():
    with open("index.html", encoding="utf-8") as f:
        html = f.read()

    old_favicon_pattern = re.compile(r'<link rel="icon"[^>]*>\n?')
    html = old_favicon_pattern.sub("", html, count=1)

    if "og:image" not in html:
        html = html.replace(
            "<title>",
            FAVICON_LINKS_ROOT + "\n" + OG_TAGS + "\n<title>",
            1,
        )
    else:
        print("index.html: OG tags already present, skipping that part.")

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("index.html: favicon + Open Graph tags updated.")


def fix_game_pages():
    files = glob.glob("games/*.html")
    patched = 0
    for path in files:
        with open(path, encoding="utf-8") as f:
            content = f.read()
        if "favicon-32x32" in content:
            continue
        old_pattern = re.compile(r'<link rel="icon"[^>]*>\n?')
        new_content = old_pattern.sub(FAVICON_LINKS_GAME_PAGE + "\n", content, count=1)
        if new_content != content:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)
            patched += 1
    print(f"Patched favicon links on {patched} game pages.")


if __name__ == "__main__":
    fix_index()
    fix_game_pages()
