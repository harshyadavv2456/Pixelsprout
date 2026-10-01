#!/usr/bin/env python3
"""
Keeps template ("fallback") guide pages out of Google's index.

Why: when Groq is unavailable, generate_guides.py writes fallback pages - the
same generic sentences with only the game name swapped. fallback_content.py
itself says these are "not meant to be published as-is for SEO". Thousands of
near-identical pages in the sitemap is exactly what Google's thin / scaled
content systems demote, and that can drag down the whole site's rankings.

What this does (safe to run every day, idempotent):
  * Template page  -> adds <meta name="robots" content="noindex,follow"> and
                      removes its URL from sitemap.xml. The page stays live and
                      its links still pass value; it just isn't indexed.
  * Real page      -> removes any noindex tag and makes sure it's in sitemap.xml.
                      (So a page upgraded later by Groq or the SEO Bot comes back
                      automatically.)

Template pages are detected by content, not by the manifest flag (the manifest
only tracks "any page of this game fell back", not which page).

Usage:
  python content-engine/seo_cleanup.py            # apply
  python content-engine/seo_cleanup.py --dry-run  # report only
"""

import argparse
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import fallback_content as fb  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAMES_INDEX_PATH = os.path.join(REPO_ROOT, "games-index.json")
MANIFEST_PATH = os.path.join(os.path.dirname(__file__), "manifest.json")
SITEMAP_PATH = os.path.join(REPO_ROOT, "sitemap.xml")
SITE = "https://playpixelsprout.com"

NOINDEX_TAG = '<meta name="robots" content="noindex,follow">'
NOINDEX_RE = re.compile(r'\s*<meta name="robots" content="noindex,follow">')

FALLBACK_FNS = {
    "tips": fb.fallback_tips,
    "controls": fb.fallback_controls,
    "beginner-guide": fb.fallback_beginner_guide,
    "similar": fb.fallback_similar_intro,
    "faq": fb.fallback_faq,
}


def template_signature(page_type, game):
    """A sentence only the fallback template produces for this game + page type."""
    content = FALLBACK_FNS[page_type](game)
    return content.get("intro") or content["faqs"][0]["answer"]


def is_template_page(page_html, page_type, game):
    sig = template_signature(page_type, game)
    return any(v in page_html for v in {sig, html.escape(sig, quote=False), html.escape(sig)})


def set_noindex(page_html, want_noindex):
    has = NOINDEX_TAG in page_html
    if want_noindex and not has:
        # Insert at the very top of <head>.
        if "<head>" not in page_html:
            return page_html, False
        return page_html.replace("<head>", "<head>\n" + NOINDEX_TAG, 1), True
    if not want_noindex and has:
        return NOINDEX_RE.sub("", page_html, count=1), True
    return page_html, False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    games = {g["slug"]: g for g in json.load(open(GAMES_INDEX_PATH, encoding="utf-8"))}
    manifest = json.load(open(MANIFEST_PATH, encoding="utf-8"))
    with open(SITEMAP_PATH, encoding="utf-8") as f:
        sitemap = f.read()

    template_urls, real_urls = set(), set()
    html_changed = 0
    for slug, entry in manifest.items():
        game = games.get(slug)
        if not game:
            continue
        for page_type, url in entry.get("pages", {}).items():
            if page_type not in FALLBACK_FNS:
                continue
            path = os.path.join(REPO_ROOT, url.strip("/"), "index.html")
            if not os.path.exists(path):
                continue
            with open(path, encoding="utf-8") as f:
                page = f.read()
            template = is_template_page(page, page_type, game)
            (template_urls if template else real_urls).add(url)
            new_page, changed = set_noindex(page, template)
            if changed:
                html_changed += 1
                if not args.dry_run:
                    with open(path, "w", encoding="utf-8", newline="\n") as f:
                        f.write(new_page)

    # Rebuild the sitemap line by line: drop template guide URLs, keep everything else.
    removed = 0
    kept_lines = []
    for line in sitemap.splitlines():
        m = re.search(r"<loc>" + re.escape(SITE) + r"(/guides/[^<]+)</loc>", line)
        if m and m.group(1) in template_urls:
            removed += 1
            continue
        kept_lines.append(line)
    new_sitemap = "\n".join(kept_lines) + ("\n" if sitemap.endswith("\n") else "")

    # Add real guide pages that are missing (e.g. upgraded since they were removed).
    missing = sorted(u for u in real_urls if f"<loc>{SITE}{u}</loc>" not in new_sitemap)
    if missing:
        entries = "\n".join(f"  <url><loc>{SITE}{u}</loc><priority>0.5</priority></url>" for u in missing)
        new_sitemap = new_sitemap.replace("</urlset>", entries + "\n</urlset>")

    if not args.dry_run and new_sitemap != sitemap:
        with open(SITEMAP_PATH, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_sitemap)

    total = len(template_urls) + len(real_urls)
    print(f"Guide pages checked: {total}")
    print(f"  real content (indexable): {len(real_urls)}")
    print(f"  template (noindex):       {len(template_urls)}")
    print(f"HTML files updated: {html_changed}")
    print(f"Sitemap: removed {removed} template URLs, added {len(missing)} real URLs")
    if args.dry_run:
        print("(dry run - nothing written)")


if __name__ == "__main__":
    main()
