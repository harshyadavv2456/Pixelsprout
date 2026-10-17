#!/usr/bin/env python3
"""
Takes games off the NOINDEX_GUIDES list (content-engine/noindex-guides.json) after
Studio has checked their played rewrite. For each slug it:
  1. removes the game's 5 guide URLs from the list,
  2. reruns seo_cleanup.py, so those pages lose the noindex tag and go back into
     sitemap.xml (a page that is still template copy stays noindex anyway),
  3. re-renders the /guides/ hub, so the game shows up in its list again.

Nothing else (apply_queue.py, the daily workflow) ever takes URLs off the list.

It refuses a page that is still the short stub written by write_stub_guides.py,
because that means no played rewrite has been published for it yet. --force skips
that check.

Usage:
  python content-engine/lift_noindex.py angry-sharks castle-defense
  python content-engine/lift_noindex.py --dry-run angry-sharks   # report only, writes nothing
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_guides as gg  # noqa: E402
import noindex_guides  # noqa: E402
import seo_cleanup  # noqa: E402

STUB_MARKERS = ("This page does not have a full ", "plays free in your browser on Pixelsprout.</p>\n<p><a href=")


def is_stub(path):
    """True if the page is still the write_stub_guides.py stub (no played rewrite yet)."""
    if not os.path.exists(path):
        return False
    with open(path, encoding="utf-8") as f:
        page = f.read()
    return any(m in page for m in STUB_MARKERS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="+")
    ap.add_argument("--dry-run", action="store_true", help="report what would change, write nothing")
    ap.add_argument("--force", action="store_true", help="lift even pages that are still stubs")
    args = ap.parse_args()

    listed = noindex_guides.load_urls()
    games = {g["slug"]: g for g in gg.load_json(gg.GAMES_INDEX_PATH, [])}
    for g in gg.load_json(os.path.join(gg.REPO_ROOT, "assets", "originals.json"), []):
        if isinstance(g, dict) and g.get("slug"):
            games.setdefault(g["slug"], g)

    to_lift, problems = [], []
    for slug in args.slugs:
        game = games.get(slug)
        if not game:
            problems.append(f"{slug}: not a game in games-index.json")
            continue
        urls = gg.guide_urls_for(game)
        on_list = [u for u in urls.values() if u in listed]
        if not on_list:
            problems.append(f"{slug}: none of its guide URLs are on the noindex list")
            continue
        stubs = [u for u in on_list if is_stub(os.path.join(gg.REPO_ROOT, u.strip("/"), "index.html"))]
        if stubs and not args.force:
            problems.append(f"{slug}: still a stub, no played rewrite published: {stubs}")
            continue
        to_lift += on_list
        print(f"{slug}: lifting {len(on_list)} URL(s): {on_list}")

    for p in problems:
        print("SKIP " + p)
    if not to_lift:
        print("Nothing to lift.")
        return 1 if problems else 0

    if args.dry_run:
        result = seo_cleanup.run(dry_run=True, forced_noindex=listed - set(to_lift))
        for u in to_lift:
            state = "indexable + in sitemap" if u in result["real_urls"] else "STAYS noindex (template copy)"
            print(f"  would be {state}: {u}")
        print(f"(dry run - list, pages, sitemap and hub untouched; {len(listed)} URLs still listed)")
        return 0

    noindex_guides.remove_urls(to_lift)
    seo_cleanup.run(dry_run=False)
    gg.write_guides_landing_page(gg.load_json(gg.GUIDES_INDEX_PATH, {}))
    print(f"Lifted {len(to_lift)} URL(s); {len(noindex_guides.load_urls())} still on the list. Hub re-rendered.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
