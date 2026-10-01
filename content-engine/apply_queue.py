#!/usr/bin/env python3
"""
Publishes guide pages written by the SEO Bot (Grok Bot) after it actually played the game.

The bot never edits HTML or pushes to main. It commits one JSON file per game to
the `seo-queue` branch, folder `seo-queue/<game-slug>.json`. The daily workflow
copies that folder into the main checkout and runs this script, which:

  1. validates every page (schema, lengths, no links, no placeholder text),
  2. HTML-escapes every string (bot text can never inject markup or scripts),
  3. renders the pages with the same templates as every other guide page,
  4. marks those page types "locked" in manifest.json so the Groq pipeline
     never overwrites them,
  5. records the result in content-engine/queue-report.json (the bot reads this
     the next day to see what was published or rejected and why).

A file is processed once per content version (tracked by SHA-256 in queue-report.json),
so the bot can fix a rejected file and push it again.

JSON format (any subset of the 5 page types is fine):
{
  "slug": "getting-over-it",
  "played": true,
  "pages": {
    "tips": {"intro": "...", "tips": ["...", ...], "conclusion": "..."},
    "controls": {"intro": "...", "desktop": "...", "mobile": "...", "tips": ["...", ...]},
    "beginner-guide": {"intro": "...", "what_it_is": "...", "first_steps": ["...", ...], "who_its_for": "..."},
    "similar": {"intro": "..."},
    "faq": {"faqs": [{"question": "...?", "answer": "..."}, ...]}
  }
}
Every page may also carry "extra_sections": [{"heading": "...", "paragraphs": ["...", ...]}].
See content-engine/SEO-BOT-QUEUE.md for the full rules.

Usage:
  python content-engine/apply_queue.py                 # reads ./seo-queue/*.json
  python content-engine/apply_queue.py --queue-dir X    # custom folder
"""

import argparse
import hashlib
import html
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import generate_guides as gg  # noqa: E402
import page_renderer as render  # noqa: E402
import similar_games as sim  # noqa: E402
import seo_cleanup  # noqa: E402
from collections_data import COLLECTIONS  # noqa: E402

REPO_ROOT = gg.REPO_ROOT
REPORT_PATH = os.path.join(os.path.dirname(__file__), "queue-report.json")
INTROS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "collection-intros.json")
COLLECTION_SLUGS = {c["slug"]: c for c in COLLECTIONS}
COLLECTION_INTRO_RULE = (150, 900)
DEFAULT_QUEUE_DIR = os.path.join(REPO_ROOT, "seo-queue")
MAX_FILES_PER_RUN = 30

# (min_chars, max_chars) for strings; (min_items, max_items, min_chars, max_chars) for lists
SCHEMAS = {
    "tips": {"intro": (40, 500), "tips": (5, 10, 30, 350), "conclusion": (20, 350)},
    "controls": {"intro": (20, 350), "desktop": (30, 600), "mobile": (30, 600), "tips": (2, 6, 20, 300)},
    "beginner-guide": {"intro": (20, 450), "what_it_is": (80, 900), "first_steps": (3, 8, 20, 300), "who_its_for": (20, 350)},
    "similar": {"intro": (120, 900)},
}
FAQ_RULES = {"count": (5, 10), "question": (10, 160), "answer": (30, 450)}
EXTRA_RULES = {"sections": (0, 4), "heading": (5, 90), "paragraphs": (1, 4), "paragraph": (60, 800)}

BANNED_PATTERNS = [
    (re.compile(r"https?://|www\.", re.I), "contains a link (links are added automatically)"),
    (re.compile(r"[<>]"), "contains < or > (no HTML allowed)"),
    (re.compile(r"\b(lorem ipsum|todo|tbd|placeholder|insert .{0,20} here|as an ai)\b", re.I), "contains placeholder/AI boilerplate text"),
    (re.compile(r"\{\{|\}\}"), "contains template braces"),
]


def check_text(value, lo, hi, where, errors):
    if not isinstance(value, str):
        errors.append(f"{where}: must be text")
        return
    v = value.strip()
    if not (lo <= len(v) <= hi):
        errors.append(f"{where}: length {len(v)} chars, must be {lo}-{hi}")
    for pattern, reason in BANNED_PATTERNS:
        if pattern.search(v):
            errors.append(f"{where}: {reason}")


def check_list(value, rule, where, errors):
    min_items, max_items, lo, hi = rule
    if not isinstance(value, list):
        errors.append(f"{where}: must be a list")
        return
    if not (min_items <= len(value) <= max_items):
        errors.append(f"{where}: {len(value)} items, must be {min_items}-{max_items}")
    for i, item in enumerate(value):
        check_text(item, lo, hi, f"{where}[{i}]", errors)
    stripped = [str(x).strip().lower() for x in value]
    if len(set(stripped)) != len(stripped):
        errors.append(f"{where}: duplicate items")


def validate_page(page_type, content):
    errors = []
    if not isinstance(content, dict):
        return [f"{page_type}: must be an object"]
    if page_type == "faq":
        faqs = content.get("faqs")
        lo, hi = FAQ_RULES["count"]
        if not isinstance(faqs, list) or not (lo <= len(faqs) <= hi):
            errors.append(f"faq.faqs: need {lo}-{hi} question/answer pairs")
        else:
            for i, qa in enumerate(faqs):
                if not isinstance(qa, dict):
                    errors.append(f"faq.faqs[{i}]: must be an object")
                    continue
                check_text(qa.get("question"), *FAQ_RULES["question"], f"faq.faqs[{i}].question", errors)
                check_text(qa.get("answer"), *FAQ_RULES["answer"], f"faq.faqs[{i}].answer", errors)
                if isinstance(qa.get("question"), str) and not qa["question"].strip().endswith("?"):
                    errors.append(f"faq.faqs[{i}].question: must end with '?'")
    else:
        for field, rule in SCHEMAS[page_type].items():
            where = f"{page_type}.{field}"
            if field not in content:
                errors.append(f"{where}: missing")
            elif len(rule) == 4:
                check_list(content[field], rule, where, errors)
            else:
                check_text(content[field], *rule, where, errors)

    extra = content.get("extra_sections", [])
    if extra:
        lo, hi = EXTRA_RULES["sections"]
        if not isinstance(extra, list) or len(extra) > hi:
            errors.append(f"{page_type}.extra_sections: max {hi} sections")
        else:
            for i, sec in enumerate(extra):
                if not isinstance(sec, dict):
                    errors.append(f"{page_type}.extra_sections[{i}]: must be an object")
                    continue
                check_text(sec.get("heading"), *EXTRA_RULES["heading"], f"{page_type}.extra_sections[{i}].heading", errors)
                paras = sec.get("paragraphs")
                plo, phi = EXTRA_RULES["paragraphs"]
                if not isinstance(paras, list) or not (plo <= len(paras) <= phi):
                    errors.append(f"{page_type}.extra_sections[{i}].paragraphs: need {plo}-{phi} paragraphs")
                else:
                    for j, para in enumerate(paras):
                        check_text(para, *EXTRA_RULES["paragraph"], f"{page_type}.extra_sections[{i}].paragraphs[{j}]", errors)
    return errors


def escape_all(value):
    """Recursively HTML-escape every string. The renderer inserts content as-is."""
    if isinstance(value, str):
        return html.escape(value.strip(), quote=True)
    if isinstance(value, list):
        return [escape_all(v) for v in value]
    if isinstance(value, dict):
        return {k: escape_all(v) for k, v in value.items()}
    return value


def handle_collection(fname, sha, item, intros, run_log, applied_hashes):
    """Collection intro files: {"collection": "<slug>", "played": true, "intro": "..."}"""
    slug = item.get("collection")
    errors = []
    if slug not in COLLECTION_SLUGS:
        errors.append(f"collection '{slug}' doesn't exist (allowed: {sorted(COLLECTION_SLUGS)})")
    elif fname != f"collection-{slug}.json":
        errors.append(f"file must be named collection-{slug}.json")
    if item.get("played") is not True:
        errors.append('"played" must be true - play several of the listed games first')
    check_text(item.get("intro"), *COLLECTION_INTRO_RULE, "intro", errors)
    applied_hashes[fname] = sha
    if errors:
        run_log["rejected"].append({"file": fname, "errors": errors[:25]})
        return
    intros[slug] = {"intro": html.escape(item["intro"].strip(), quote=True), "source": "bot",
                    "updated_at": run_log["ran_at"]}
    run_log["published"].append({"file": fname, "collection": slug,
                                 "urls": [f"https://playpixelsprout.com/games-like/{slug}/"]})


def file_sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue-dir", default=DEFAULT_QUEUE_DIR)
    args = parser.parse_args()

    report = gg.load_json(REPORT_PATH, {"applied_hashes": {}, "runs": []})
    applied_hashes = report.setdefault("applied_hashes", {})

    if not os.path.isdir(args.queue_dir):
        print(f"No queue folder at {args.queue_dir} - nothing to publish.")
        return

    files = sorted(f for f in os.listdir(args.queue_dir) if f.endswith(".json"))
    pending = [f for f in files if applied_hashes.get(f) != file_sha(os.path.join(args.queue_dir, f))]
    if not pending:
        print("SEO queue: no new or changed files.")
        return
    pending = pending[:MAX_FILES_PER_RUN]

    all_games = gg.load_json(gg.GAMES_INDEX_PATH, [])
    games_by_slug = {g["slug"]: g for g in all_games}
    sim.build_index(all_games)
    manifest = gg.load_json(gg.MANIFEST_PATH, {})
    guides_index = gg.load_json(gg.GUIDES_INDEX_PATH, {})

    run_log = {"ran_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "published": [], "rejected": []}
    intros = gg.load_json(INTROS_PATH, {})
    intros_before = json.dumps(intros, sort_keys=True)
    touched_slugs = []

    for fname in pending:
        path = os.path.join(args.queue_dir, fname)
        sha = file_sha(path)
        try:
            with open(path, encoding="utf-8") as f:
                item = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            run_log["rejected"].append({"file": fname, "errors": [f"invalid JSON: {e}"]})
            applied_hashes[fname] = sha
            continue

        if isinstance(item, dict) and "collection" in item:
            handle_collection(fname, sha, item, intros, run_log, applied_hashes)
            continue

        slug = item.get("slug") if isinstance(item, dict) else None
        errors = []
        if not slug or slug not in games_by_slug:
            errors.append(f"slug '{slug}' is not a game in games-index.json")
        elif fname != f"{slug}.json":
            errors.append(f"file must be named {slug}.json")
        if not isinstance(item, dict) or item.get("played") is not True:
            errors.append('"played" must be true - only publish games you actually played')
        pages = item.get("pages") if isinstance(item, dict) else None
        if not isinstance(pages, dict) or not pages:
            errors.append('"pages" must contain at least one page type')
            pages = {}
        unknown = [p for p in pages if p not in gg.GUIDE_PAGE_TYPES]
        if unknown:
            errors.append(f"unknown page types: {unknown} (allowed: {gg.GUIDE_PAGE_TYPES})")

        page_errors = {}
        if not errors:
            for page_type, content in pages.items():
                errs = validate_page(page_type, content)
                if not errs:
                    game = games_by_slug[slug]
                    sig = seo_cleanup.template_signature(page_type, game)
                    if sig.lower() in json.dumps(content, ensure_ascii=False).lower():
                        errs = [f"{page_type}: copies the generic template text"]
                if errs:
                    page_errors[page_type] = errs

        good_pages = {p: c for p, c in pages.items() if p not in page_errors} if not errors else {}
        if errors or not good_pages:
            all_errs = errors + [e for errs in page_errors.values() for e in errs]
            run_log["rejected"].append({"file": fname, "errors": all_errs[:25]})
            applied_hashes[fname] = sha
            continue

        game = games_by_slug[slug]
        related = sim.find_similar(game, all_games, limit=8)
        category_url = gg.category_url_for(game)
        page_urls = gg.guide_urls_for(game)
        for page_type, content in good_pages.items():
            out_dir = os.path.join(REPO_ROOT, page_urls[page_type].strip("/"))
            os.makedirs(out_dir, exist_ok=True)
            page_html = render.render_guide_page(page_type, game, escape_all(content), related, page_urls, category_url)
            with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8", newline="\n") as f:
                f.write(page_html)

        entry = manifest.get(slug) or {"pages": page_urls, "any_fallback": True}
        locked = sorted(set(entry.get("locked", [])) | set(good_pages))
        entry["locked"] = locked
        entry["pages"] = page_urls
        entry["bot_updated_at"] = run_log["ran_at"]
        # Still "fallback" if any page the bot didn't cover is template text.
        still_template = False
        for page_type in gg.GUIDE_PAGE_TYPES:
            if page_type in locked:
                continue
            p = os.path.join(REPO_ROOT, page_urls[page_type].strip("/"), "index.html")
            if not os.path.exists(p):
                still_template = True
                continue
            with open(p, encoding="utf-8") as f:
                if seo_cleanup.is_template_page(f.read(), page_type, game):
                    still_template = True
        entry["any_fallback"] = still_template
        manifest[slug] = entry
        guides_index[slug] = page_urls
        touched_slugs.append(slug)

        published = {"file": fname, "slug": slug, "pages": sorted(good_pages),
                     "urls": [f"https://playpixelsprout.com{page_urls[p]}" for p in sorted(good_pages)]}
        if page_errors:
            published["rejected_pages"] = {p: e[:10] for p, e in page_errors.items()}
        run_log["published"].append(published)
        applied_hashes[fname] = sha

    gg.save_json(gg.MANIFEST_PATH, manifest)
    gg.save_json(gg.GUIDES_INDEX_PATH, guides_index)
    if json.dumps(intros, sort_keys=True) != intros_before:
        gg.save_json(INTROS_PATH, intros)  # generate_collections.py renders these on its next step
    if touched_slugs:
        gg.refresh_game_pages(touched_slugs, all_games, guides_index)

    report["runs"] = ([run_log] + report.get("runs", []))[:30]  # keep the last 30 runs
    gg.save_json(REPORT_PATH, report)

    print(f"SEO queue: published {len(run_log['published'])} file(s), rejected {len(run_log['rejected'])}.")
    for r in run_log["rejected"]:
        print(f"  REJECTED {r['file']}: {r['errors'][:3]}")


if __name__ == "__main__":
    main()
