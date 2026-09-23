#!/usr/bin/env python3
"""Moves every existing page onto the shared shell (site_shell / site_pages).

Idempotent: each page is read back into its fields (old template or the
current one) and re-rendered, so running it twice gives the same output.

  python migrate-ui.py --dry-run                 # validate everything, write nothing
  python migrate-ui.py --only games --limit 5    # first 5 game pages
  python migrate-ui.py --only games,guides --sample-dir qa/samples
  python migrate-ui.py                           # everything

Types: catalog, games, guides, collections, legal, tools, categories, hub, home
"""

import argparse
import glob
import json
import os
import re
import sys

import site_pages as P
import site_shell as S

ROOT = S.ROOT
TYPES = ["catalog", "games", "guides", "collections", "legal", "tools", "categories", "hub", "home"]
NATIVE_GAMES = {"memory", "pong", "snake", "tetris", "tictactoe"}
FILE_FILTER = None


def selected(files):
    if FILE_FILTER is None:
        return files
    return [f for f in files if os.path.normcase(f) in FILE_FILTER]


class Stats:
    def __init__(self):
        self.written = {}
        self.unchanged = {}
        self.errors = []

    def ok(self, kind, changed):
        bucket = self.written if changed else self.unchanged
        bucket[kind] = bucket.get(kind, 0) + 1


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, content, args, stats, kind, original=None):
    changed = original != content
    if args.sample_dir and changed:
        rel = os.path.relpath(path, ROOT).replace(os.sep, "__")
        os.makedirs(args.sample_dir, exist_ok=True)
        with open(os.path.join(args.sample_dir, rel), "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
    if changed and not args.dry_run:
        P._write(path, content)
    stats.ok(kind, changed)


def require(cond, message):
    if not cond:
        raise AssertionError(message)


def _jsonld_types(blocks):
    types = []
    for b in blocks:
        try:
            types.append(json.loads(b).get("@type"))
        except ValueError:
            types.append("unparseable")
    return types


# ---------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------

def legacy_home_thumbs():
    doc = read(os.path.join(ROOT, "index.html"))
    if "data-grid" not in doc:
        return {}
    thumbs = {}
    for slug, inner in re.findall(r'<a class="card[^"]*" href="games/([^"]+)\.html"[^>]*>(.*?)</a>', doc, re.DOTALL):
        img = re.search(r'<img[^>]*src="([^"]+)"', inner)
        if img and slug not in thumbs:
            thumbs[slug] = img.group(1)
    return thumbs


def rebuild_catalog(args, stats):
    path = os.path.join(ROOT, "games-index.json")
    raw = json.load(open(path, encoding="utf-8"))
    catalog = S.load_catalog(path)
    by_slug = {g["slug"]: g for g in catalog}
    home_thumbs = legacy_home_thumbs()
    added = filled = 0
    for file in sorted(glob.glob(os.path.join(ROOT, "games", "*.html"))):
        slug = os.path.basename(file)[:-5]
        if slug in NATIVE_GAMES:
            continue
        fields = P.extract_game_page(read(file), slug)
        if not fields:
            continue
        thumb = fields["thumbnail"] or home_thumbs.get(slug, "")
        entry = by_slug.get(slug)
        if entry is None:
            entry = {"slug": slug, "title": fields["title"], "category": fields["category"], "thumbnail": thumb}
            if "gamemonetize" in fields["embed_url"]:
                entry["source"] = "gamemonetize"
            catalog.append(entry)
            by_slug[slug] = entry
            added += 1
        elif not entry.get("thumbnail") and thumb:
            entry["thumbnail"] = thumb
            filled += 1
    print(f"catalog: {len(raw)} entries -> {len(catalog)} unique ({len(raw) - (len(catalog) - added)} duplicates dropped, {added} missing games added, {filled} thumbnails filled)")
    content = json.dumps(catalog)
    original = read(path)
    write(path, content, args, stats, "catalog", original)
    return catalog


# ---------------------------------------------------------------------------
# Page types
# ---------------------------------------------------------------------------

def migrate_games(args, stats, catalog, guides_index):
    by_slug = {g["slug"]: g for g in catalog}
    files = sorted(glob.glob(os.path.join(ROOT, "games", "*.html")))
    files = selected(files)
    if args.limit:
        files = files[: args.limit]
    for file in files:
        slug = os.path.basename(file)[:-5]
        try:
            doc = read(file)
            fields = P.extract_game_page(doc, slug)
            if fields is None:
                out = P.wrap_legacy_page(doc, total_games=len(catalog))
                require('class="topbar"' in out and "</main>" in out, "legacy wrap failed")
                write(file, out, args, stats, "games(native)", doc)
                continue
            if not fields["thumbnail"] and by_slug.get(slug, {}).get("thumbnail"):
                fields["thumbnail"] = by_slug[slug]["thumbnail"]
            require(fields["title"], "missing title")
            require(fields["title_tag"], "missing <title>")
            require(fields["meta_desc"] is not None, "missing meta description")
            out = P.render_game_page(fields, catalog, guides=guides_index.get(slug), total_games=len(catalog))
            require(f'<iframe src="{fields["embed_url"]}"' in out, "embed URL lost")
            require(f"<title>{fields['title_tag']}</title>" in out, "<title> changed")
            require(_jsonld_types(P._jsonld_blocks(out)) == _jsonld_types(P._jsonld_blocks(doc)), "JSON-LD types changed")
            require("games\\\\" not in out, "Windows path left in JSON-LD")
            require("fullscreen_click" in out, "fullscreen GA event lost")
            if "screen.orientation.lock" in doc:
                require("screen.orientation.lock" in out, "orientation lock lost")
            again = P.extract_game_page(out, slug)
            require(again["description_html"] == (fields["description_html"] or again["description_html"]), "description not round-trippable")
            write(file, out, args, stats, "games", doc)
        except Exception as e:  # noqa: BLE001 - report and continue
            stats.errors.append(f"{file}: {e}")


def migrate_guides(args, stats, catalog):
    by_slug = {g["slug"]: g for g in catalog}
    files = sorted(glob.glob(os.path.join(ROOT, "guides", "*", "index.html")))
    files = selected(files)
    if args.limit:
        files = files[: args.limit]
    for file in files:
        try:
            doc = read(file)
            f = P.extract_guide_page(doc)
            require(f["h1"], "missing h1")
            require(text_len(f["body"]) > 20, "empty guide body")
            require(f["canonical"], "missing canonical")
            out = P.render_guide_page(f, by_slug, total_games=len(catalog))
            require(f'<link rel="canonical" href="{f["canonical"]}">' in out, "canonical changed")
            require(_jsonld_types(P._jsonld_blocks(out)) == _jsonld_types(P._jsonld_blocks(doc)), "JSON-LD types changed")
            require(out.count('class="ad ') <= 3, "more than 3 ad units")
            again = P.extract_guide_page(out)
            require(again["body"] == f["body"], "guide body not round-trippable")
            write(file, out, args, stats, "guides", doc)
        except Exception as e:  # noqa: BLE001
            stats.errors.append(f"{file}: {e}")


def text_len(fragment):
    return len(S.text(fragment))


def migrate_collections(args, stats, catalog):
    by_slug = {g["slug"]: g for g in catalog}
    files = sorted(glob.glob(os.path.join(ROOT, "games-like", "*", "index.html")))
    files = selected(files)
    if args.limit:
        files = files[: args.limit]
    for file in files:
        try:
            doc = read(file)
            f = P.extract_collection_page(doc)
            require(f["h1"] and f["games"], "missing h1 or games")
            out = P.render_collection_page(f, by_slug, total_games=len(catalog))
            require(f'<link rel="canonical" href="{f["canonical"]}">' in out, "canonical changed")
            require(_jsonld_types(P._jsonld_blocks(out)) == _jsonld_types(P._jsonld_blocks(doc)), "JSON-LD types changed")
            write(file, out, args, stats, "collections", doc)
        except Exception as e:  # noqa: BLE001
            stats.errors.append(f"{file}: {e}")


def migrate_legal(args, stats, catalog):
    for name in ["about.html", "contact.html", "privacy.html", "terms.html"]:
        file = os.path.join(ROOT, name)
        try:
            doc = read(file)
            f = P.extract_legal_page(doc)
            require(f["h1"] and text_len(f["body"]) > 50, "missing content")
            out = P.render_legal_page(f, total_games=len(catalog))
            write(file, out, args, stats, "legal", doc)
        except Exception as e:  # noqa: BLE001
            stats.errors.append(f"{file}: {e}")


def migrate_tools(args, stats, catalog):
    for name in ["cold-read", "gift-file"]:
        file = os.path.join(ROOT, name, "index.html")
        try:
            doc = read(file)
            out = P.wrap_legacy_page(doc, total_games=len(catalog), active=f"/{name}/")
            require(out.count('class="topbar"') == 1, "shell duplicated")
            write(file, out, args, stats, "tools", doc)
        except Exception as e:  # noqa: BLE001
            stats.errors.append(f"{file}: {e}")


def migrate_categories(args, stats, catalog):
    pages = P.build_category_pages(catalog, write=False)
    for path, out in pages.items():
        original = read(path) if os.path.exists(path) else None
        if original:
            old_canon = re.search(r'<link rel="canonical" href="([^"]*)"', original)
            if old_canon and f'<link rel="canonical" href="{old_canon.group(1)}">' not in out:
                stats.errors.append(f"{path}: canonical changed")
                continue
        write(path, out, args, stats, "categories", original)


def migrate_hub(args, stats, catalog):
    path = os.path.join(ROOT, "guides", "index.html")
    write(path, P.render_guides_hub(total_games=len(catalog)), args, stats, "hub", read(path))


def migrate_home(args, stats, catalog):
    for path, out in P.build_home(catalog, write=False).items():
        original = read(path) if os.path.exists(path) else None
        write(path, out, args, stats, "home", original)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="validate and report, write nothing")
    ap.add_argument("--limit", type=int, default=0, help="max pages per type")
    ap.add_argument("--only", default="", help="comma-separated types: " + ",".join(TYPES))
    ap.add_argument("--sample-dir", default="", help="also copy every rendered page here for review")
    ap.add_argument("--files", default="", help="text file listing repo-relative paths; games/guides/collections are limited to these")
    args = ap.parse_args()

    only = [t.strip() for t in args.only.split(",") if t.strip()] or TYPES
    global FILE_FILTER
    if args.files:
        with open(args.files, encoding="utf-8") as fh:
            FILE_FILTER = {os.path.normcase(os.path.join(ROOT, l.strip())) for l in fh if l.strip()}
    unknown = set(only) - set(TYPES)
    if unknown:
        ap.error(f"unknown types: {', '.join(sorted(unknown))}")

    stats = Stats()
    if "catalog" in only:
        catalog = rebuild_catalog(args, stats)
        if args.dry_run:
            print("  (dry run: later steps use the rebuilt catalog in memory)")
    else:
        catalog = S.load_catalog()
    guides_index = json.load(open(os.path.join(ROOT, "guides-index.json"), encoding="utf-8"))

    steps = {
        "games": lambda: migrate_games(args, stats, catalog, guides_index),
        "guides": lambda: migrate_guides(args, stats, catalog),
        "collections": lambda: migrate_collections(args, stats, catalog),
        "legal": lambda: migrate_legal(args, stats, catalog),
        "tools": lambda: migrate_tools(args, stats, catalog),
        "categories": lambda: migrate_categories(args, stats, catalog),
        "hub": lambda: migrate_hub(args, stats, catalog),
        "home": lambda: migrate_home(args, stats, catalog),
    }
    for t in TYPES:
        if t in only and t in steps:
            print(f"-> {t}")
            steps[t]()

    print("\nSummary" + (" (dry run, nothing written)" if args.dry_run else ""))
    for kind in sorted(set(stats.written) | set(stats.unchanged)):
        print(f"  {kind:14} changed {stats.written.get(kind, 0):6}   unchanged {stats.unchanged.get(kind, 0):6}")
    if stats.errors:
        print(f"\n{len(stats.errors)} error(s):")
        for e in stats.errors[:40]:
            print("  " + e)
        sys.exit(1)


if __name__ == "__main__":
    main()
