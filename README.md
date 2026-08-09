# Adsterra Integration — Deployment Steps

## What's in this folder
Only the files that were actually changed, so you can drop them straight
into your real local repo without a messy full-repo diff:

- `inject-adsterra.py` — NEW. One-time bulk script, retrofits all existing
  pages. Idempotent (safe to re-run).
- `auto-add-games.py`, `auto-add-gamemonetize.py` — daily-cron templates
  (GamePix / GameMonetize), now include Adsterra for all *future* games.
- `bulk-add-games.py`, `bulk-add-gamemonetize.py` — your manual one-time
  bulk-import scripts, updated to match.
- `content-engine/page_renderer.py` — guide + collection page template
  (used by `generate_guides.py` / `generate_collections.py`, also on a
  daily cron). Now includes Adsterra for all future guide/collection pages.

## What was NOT touched (verified)
- `ads.txt` — untouched, your AdSense line is still there.
- `index.html` (homepage) — untouched, zero ads, as you asked.
- All existing AdSense `<ins class="adsbygoogle">` slots and scripts —
  untouched, still firing exactly as before.
- Category landing pages (`board/`, `ball/`, `soccer/`, etc.) — not in
  scope, left alone.

## Placement logic
- **Game pages** (`games/*.html`): Adsterra 300x250 banner + 728x90 banner
  (both additive, next to existing AdSense slots) + the Popunder script
  loaded in `<head>`. Adsterra's popunder attaches its own click listener
  site-wide once loaded — since it's only on game pages, it effectively
  fires on the Play/Fullscreen click, not on page load.
- **Guide pages** (`guides/*/index.html`) and **collection pages**
  (`games-like/*/index.html`): 728x90 near the top, 300x250 near the
  bottom. No popunder on these (matches what you asked — popunder only on
  the "opening a game" moment).

## Deploy steps
1. Copy these 6 files into your real local repo at the matching paths
   (overwrite the existing ones at the same relative locations).
2. Copy `inject-adsterra.py` into your repo root.
3. From your repo root, run:
   ```
   python inject-adsterra.py
   ```
   This retrofits all ~4,842 existing game pages, ~13,824 guide pages, and
   26 collection pages in place. It prints a summary of how many files were
   updated. Safe to re-run — already-patched files are skipped.
4. Review `git diff` on a couple of sample files (e.g. `games/<any-game>.html`)
   to confirm it looks right.
5. `git add -A && git commit -m "Add Adsterra ad units (banner 300x250, 728x90, popunder)" && git push`
6. GitHub Actions / Vercel deploy takes it from there — no other changes
   needed for the daily automation, since the templates are now updated
   too.

## Verified before handoff
- All 5 edited Python files pass `python3 -m py_compile`.
- `page_renderer.py` was actually executed end-to-end (rendered a sample
  guide page and a sample collection page) to confirm no f-string/brace
  errors and that both Adsterra blocks render correctly alongside the
  existing AdSense blocks.
- Ran `inject-adsterra.py` against the full uploaded codebase: 4842/4842
  game pages, 13824/13824 guide pages, 26/26 collection pages updated on
  first pass, 0/0/0 on re-run (confirms idempotency).
